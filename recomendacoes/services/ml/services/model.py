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
        self.expected_features: list[str] | None = None
        self._load_or_train()

    @classmethod
    def instance(cls) -> "PriceModel":
        if cls._instance is None:
            cls._instance = PriceModel()
        return cls._instance

    def _load_or_train(self):
        data = [d for d in iter_flattened() if d['preco_aluguel'] > 0 and d['area_m2'] > 0]
        if SKLEARN_OK:
            # 1) tentar carregar modelo centralizado (treinado por aluga_ai_web/ml)
            try:
                from pathlib import Path
                # procurar a raiz do repositório (onde está manage.py)
                cur = Path(__file__).resolve()
                repo_root = None
                for p in list(cur.parents):
                    if (p / 'manage.py').exists():
                        repo_root = p
                        break
                if repo_root is not None:
                    # possíveis locais de modelo treinado (prioridades)
                    candidates = [
                        repo_root / 'recomendacoes' / 'services' / 'ml' / 'model_store' / 'price_model.joblib',
                        repo_root / 'recomendacoes' / 'models' / 'model.pkl',
                        repo_root / 'aluga_ai_web' / 'ml' / 'models' / 'model.pkl',
                    ]
                    for shared_model in candidates:
                        try:
                            if shared_model.exists():
                                self.pipeline = joblib.load(shared_model)
                                self.method = 'ml'
                                # try to load metadata with feature names if available
                                try:
                                    meta_path = shared_model.parent / 'metadata.json'
                                    if meta_path.exists():
                                        import json
                                        with open(meta_path, 'r', encoding='utf-8') as mf:
                                            meta = json.load(mf)
                                            self.expected_features = meta.get('features')
                                except Exception:
                                    self.expected_features = None
                                # try to load label encoders and scaler saved alongside the model
                                try:
                                    le_path = shared_model.parent / 'label_encoders.pkl'
                                    sc_path = shared_model.parent / 'scaler.pkl'
                                    if le_path.exists():
                                        self.label_encoders = joblib.load(le_path)
                                    if sc_path.exists():
                                        self.scaler = joblib.load(sc_path)
                                except Exception:
                                    pass
                                # fallback to sklearn attribute
                                try:
                                    if hasattr(self.pipeline, 'feature_names_in_'):
                                        self.expected_features = list(self.pipeline.feature_names_in_.tolist())
                                except Exception:
                                    pass
                                return
                        except Exception:
                            self.pipeline = None

            except Exception:
                # se algo falhar buscando o model central, continuar
                pass

            # 2) tentar carregar cache local do app
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
            # Build DataFrame with the expected features (fill missing with sensible defaults)
            if self.expected_features is None:
                # fallback to a minimal set
                cols = ['tipo', 'cidade', 'area_m2', 'quartos', 'banheiros', 'vagas_garagem', 'condominio', 'iptu']
            else:
                cols = list(self.expected_features)

            row = {}
            for c in cols:
                if c in ('tipo', 'cidade', 'politica_cancelamento', 'endereco_bairro'):
                    row[c] = features.get(c) or ''
                elif c in ('mobiliado', 'wifi', 'loc_estrategica', 'anfitriao_superhost'):
                    row[c] = int(bool(features.get(c)))
                else:
                    # numeric fallback
                    try:
                        row[c] = float(features.get(c) or 0.0)
                    except Exception:
                        row[c] = 0.0

            X = pd.DataFrame([row], columns=cols)

            # If underlying estimator is a plain sklearn regressor (not a pipeline),
            # ensure categorical features are encoded and numeric features scaled
            try:
                import numpy as _np
                est = self.pipeline
                if not hasattr(est, 'named_steps'):
                    # prepare row vector in expected order
                    feat_order = cols
                    vec = []
                    cat_keys = set(self.label_encoders.keys()) if isinstance(self.label_encoders, dict) else set()
                    for f in feat_order:
                        if f in cat_keys:
                            le = self.label_encoders.get(f)
                            val = str(row.get(f) or '')
                            try:
                                enc = int(le.transform([val])[0])
                            except Exception:
                                # unseen category -> map to 0
                                try:
                                    enc = int(le.transform([le.classes_[0]])[0])
                                except Exception:
                                    enc = 0
                            vec.append(enc)
                        else:
                            try:
                                vec.append(float(row.get(f) or 0.0))
                            except Exception:
                                vec.append(0.0)

                    arr = _np.asarray([vec], dtype=float)
                    # apply scaler to numeric columns if scaler exists
                    if getattr(self, 'scaler', None) is not None:
                        # determine numeric indices: those not in cat_keys
                        numeric_idx = [i for i, f in enumerate(feat_order) if f not in cat_keys]
                        # slice numeric columns and scale
                        num_part = arr[:, numeric_idx]
                        try:
                            scaled = self.scaler.transform(num_part)
                            arr[:, numeric_idx] = scaled
                        except Exception:
                            # if scaling fails, continue with unscaled
                            pass

                    # use arr for prediction
                    pred = float(est.predict(arr)[0])
                    details = None
                    return pred, 'ml', details
            except Exception:
                # fallback to generic pipeline predict below
                pass
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
            # logar a predição para monitoramento
            try:
                from recomendacoes.services.ml.monitoring import log_prediction
                metadata = {'features': self.expected_features} if self.expected_features else None
                log_prediction({k: features.get(k) for k in X.columns.tolist()}, pred, 'ml', details=details, metadata=metadata)
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
        # log baseline também
        try:
            from recomendacoes.services.ml.monitoring import log_prediction
            log_prediction(features, pred, 'baseline', details=(details if return_details else None), metadata={'method': 'baseline'})
        except Exception:
            pass
        return pred, "baseline", (details if return_details else None)
