import os
from typing import Dict, Tuple, Optional

from .data_loader import iter_flattened

try:
    import joblib
    import pandas as pd
    from sklearn.compose import ColumnTransformer
    from sklearn.pipeline import Pipeline
    from sklearn.preprocessing import OneHotEncoder, StandardScaler
    from sklearn.ensemble import RandomForestRegressor
    SKLEARN_OK = True
except Exception:
    SKLEARN_OK = False
    joblib = None  # type: ignore

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, 'model_store')
MODEL_PATH = os.path.join(MODEL_DIR, 'price_model.joblib')

CAT = ['tipo', 'cidade']  # do JSON
NUM = ['area_m2', 'quartos', 'banheiros', 'vagas_garagem', 'condominio', 'iptu']

def _ensure_dirs():
    os.makedirs(MODEL_DIR, exist_ok=True)

class _Baseline:
    # Regressão sequencial simples em Python puro
    def __init__(self):
        self.k_area = 45.0
        self.k_q = 300.0
        self.k_b = 220.0
        self.k_v = 180.0
        self.bias_overall = 1000.0
        self.bias_city = {}
        self.bias_tipo = {}

    @staticmethod
    def _median(seq):
        s = sorted(seq)
        n = len(s)
        if n == 0:
            return 0.0
        mid = n // 2
        return float((s[mid - 1] + s[mid]) / 2.0) if n % 2 == 0 else float(s[mid])

    @staticmethod
    def _slope(x, y):
        n = len(x)
        if n == 0:
            return 0.0
        mx = sum(x) / n
        my = sum(y) / n
        varx = sum((v - mx) ** 2 for v in x)
        if varx == 0:
            return 0.0
        cov = sum((vx - mx) * (vy - my) for vx, vy in zip(x, y))
        return cov / varx

    def fit(self, data):
        data = [d for d in data if d['area_m2'] > 0 and d['preco_aluguel'] > 0]
        if not data:
            return self

        self.k_area = float(self._median([d['preco_aluguel'] / max(d['area_m2'], 1.0) for d in data]))
        res1 = [d['preco_aluguel'] - self.k_area * d['area_m2'] for d in data]

        self.k_q = self._slope([d['quartos'] for d in data], res1)
        res2 = [r - self.k_q * d['quartos'] for r, d in zip(res1, data)]

        self.k_b = self._slope([d['banheiros'] for d in data], res2)
        res3 = [r - self.k_b * d['banheiros'] for r, d in zip(res2, data)]

        self.k_v = self._slope([d['vagas_garagem'] for d in data], res3)
        res4 = [r - self.k_v * d['vagas_garagem'] for r, d in zip(res3, data)]

        self.bias_overall = float(self._median(res4)) if res4 else 0.0

        # deltas por cidade/tipo
        by_city = {}
        by_tipo = {}
        for d, r in zip(data, res4):
            by_city.setdefault(d['cidade'], []).append(r)
            by_tipo.setdefault(d['tipo'], []).append(r)

        self.bias_city = {c: float(self._median(vals) - self.bias_overall) for c, vals in by_city.items() if vals}
        self.bias_tipo = {t: float(self._median(vals) - self.bias_overall) for t, vals in by_tipo.items() if vals}
        return self

    def predict(self, X: Dict) -> float:
        tipo = X.get('tipo')
        cidade = X.get('cidade')
        area = float(X.get('area_m2') or 0.0)
        q = int(X.get('quartos') or 0)
        b = int(X.get('banheiros') or 0)
        v = int(X.get('vagas_garagem') or 0)

        val = (
            self.k_area * area
            + self.k_q * q
            + self.k_b * b
            + self.k_v * v
            + self.bias_overall
            + (self.bias_city.get(cidade, 0.0) if cidade else 0.0)
            + (self.bias_tipo.get(tipo, 0.0) if tipo else 0.0)
        )
        return max(0.0, float(val))

class PriceModel:
    _instance: Optional["PriceModel"] = None

    def __init__(self):
        _ensure_dirs()
        self.method = "baseline"
        self.pipeline = None
        self.baseline = _Baseline()
        self._load_or_train()

    @classmethod
    def instance(cls) -> "PriceModel":
        if cls._instance is None:
            cls._instance = PriceModel()
        return cls._instance

    def _load_or_train(self):
        data = [d for d in iter_flattened() if d['preco_aluguel'] > 0 and d['area_m2'] > 0]
        if SKLEARN_OK:
            # tentar carregar cache
            if os.path.exists(MODEL_PATH):
                try:
                    self.pipeline = joblib.load(MODEL_PATH)  # type: ignore
                    self.method = "ml"
                    return
                except Exception:
                    self.pipeline = None

            # treinar
            try:
                import pandas as pd  # type: ignore
                from sklearn.compose import ColumnTransformer  # type: ignore
                from sklearn.pipeline import Pipeline  # type: ignore
                from sklearn.preprocessing import OneHotEncoder, StandardScaler  # type: ignore
                from sklearn.ensemble import RandomForestRegressor  # type: ignore

                df = pd.DataFrame(data)
                X = df[CAT + NUM]
                y = df['preco_aluguel'].astype(float)

                pre = ColumnTransformer(
                    transformers=[
                        ("cat", OneHotEncoder(handle_unknown="ignore"), CAT),
                        ("num", Pipeline(steps=[("scaler", StandardScaler())]), NUM),
                    ],
                    remainder="drop",
                )
                rf = RandomForestRegressor(n_estimators=180, random_state=42, n_jobs=-1)
                pipe = Pipeline(steps=[("pre", pre), ("rf", rf)])
                pipe.fit(X, y)
                self.pipeline = pipe
                self.method = "ml"
                try:
                    joblib.dump(pipe, MODEL_PATH)  # type: ignore
                except Exception:
                    pass
            except Exception:
                self.pipeline = None
                self.method = "baseline"

        # baseline sempre disponível
        self.baseline.fit(data)

    def predict(self, features: Dict, return_details: bool = False) -> Tuple[float, str, Optional[Dict]]:
        if self.pipeline is not None and self.method == "ml":
            # predição via sklearn
            import pandas as pd  # type: ignore
            X = pd.DataFrame([{
                'tipo': features.get('tipo'),
                'cidade': features.get('cidade'),
                'area_m2': float(features.get('area_m2') or 0.0),
                'quartos': int(features.get('quartos') or 0),
                'banheiros': int(features.get('banheiros') or 0),
                'vagas_garagem': int(features.get('vagas_garagem') or 0),
                'condominio': float(features.get('condominio') or 0.0),
                'iptu': float(features.get('iptu') or 0.0),
            }])
            pred = float(self.pipeline.predict(X)[0])
            details = None
            # se RandomForest, opcionalmente expor desvio dos estimadores
            try:
                import numpy as np  # type: ignore
                rf = self.pipeline.named_steps.get("rf")
                if hasattr(rf, "estimators_"):
                    Xt = self.pipeline.named_steps["pre"].transform(X)
                    preds = np.array([t.predict(Xt)[0] for t in rf.estimators_])
                    details = {"std_pred": float(np.std(preds))}
            except Exception:
                pass
            return pred, "ml", details
        # fallback
        pred = self.baseline.predict(features)
        details = {
            "k_area": self.baseline.k_area,
            "k_quartos": self.baseline.k_q,
            "k_banheiros": self.baseline.k_b,
            "k_vagas": self.baseline.k_v,
            "bias_overall": self.baseline.bias_overall,
        }
        return pred, "baseline", (details if return_details else None)
