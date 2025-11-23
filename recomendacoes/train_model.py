import argparse
import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# Util
# -----------------------------------------------------------------------------
def project_root() -> Path:
    """
    Retorna a raiz do projeto a partir deste arquivo.
    Evita problemas quando __file__ não existe (ex.: notebooks).
    """
    try:
        return Path(__file__).resolve().parent
    except NameError:
        # Fallback: diretório atual
        return Path.cwd()


# -----------------------------------------------------------------------------
# Trainer
# -----------------------------------------------------------------------------
class ModelTrainer:
    """Treina modelo para predição de preços de imóveis."""

    def __init__(self):
        # localizar raiz do repositório (onde está manage.py)
        from pathlib import Path
        cur = Path(__file__).resolve()
        repo_root = None
        for p in list(cur.parents):
            if (p / 'manage.py').exists():
                repo_root = p
                break
        if repo_root is None:
            repo_root = Path.cwd()

        # ETL outputs agora em /dados/processed
        self.etl_dir = (repo_root / "dados" / "processed").resolve()

        # salvar artefatos do treino no model_store do app recomendacoes
        self.ml_dir = (repo_root / "recomendacoes" / "services" / "ml" / "model_store").resolve()
        self.ml_dir.mkdir(parents=True, exist_ok=True)

        self.label_encoders: dict[str, LabelEncoder] = {}
        self.scaler = StandardScaler()
        self.model = RandomForestRegressor(
            n_estimators=300,
            max_depth=None,
            min_samples_split=2,
            random_state=42,
            n_jobs=-1,
        )

        # Para execução opcional de Grid Search
        self.grid_results = {}
        self.best_model = None
        self.best_params = None

    # ------------------------------- Data ------------------------------------
    def get_latest_etl_file(self) -> Path:
        """Obtém o arquivo CSV mais recente do ETL."""
        csv_files = sorted(self.etl_dir.glob("imoveis_processed_*.csv"), key=lambda p: p.stat().st_mtime)
        if not csv_files:
            msg = (
                f"\nERRO: Nenhum arquivo processado encontrado em {self.etl_dir}\n\n"
                "Soluções:\n"
                "1. cd aluga_ai_web/Dados && python etl.py\n"
                "2. ou: cd aluga_ai_web/ML && python run_pipeline.py\n"
            )
            logger.error(msg)
            raise FileNotFoundError(msg)
        return csv_files[-1]

    def prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Prepara features para o modelo (numéricas + categóricas)."""
        logger.info("Preparando features...")

        base_cols = [
            "tipo", "quartos", "banheiros", "vagas_garagem", "area_m2",
            "mobiliado", "wifi", "distancia_metro_km", "distancia_onibus_km",
            "max_hospedes", "tempo_anuncio_meses", "ano_construcao", "andar",
            "condominio", "iptu", "nota_media", "num_comodidades", "num_fotos",
            "num_avaliacoes", "num_regras", "num_tags", "loc_estrategica",
            "quality_score",
        ]

        optional_cols = ["endereco_cidade", "endereco_bairro", "politica_cancelamento", "anfitriao_superhost"]

        feature_columns = [c for c in base_cols if c in df.columns] + [c for c in optional_cols if c in df.columns]
        missing_target = "preco_aluguel" not in df.columns

        if missing_target:
            raise ValueError("A coluna alvo 'preco_aluguel' não está presente no dataset processado.")

        df_features = df[feature_columns + ["preco_aluguel"]].copy()

        # Garantir tipos consistentes
        # Booleans para int (0/1)
        for bcol in ["mobiliado", "wifi", "loc_estrategica", "anfitriao_superhost"]:
            if bcol in df_features.columns:
                df_features[bcol] = df_features[bcol].astype(float).fillna(0).astype(int)

        df_features = df_features.fillna(0)

        # Encoding de categóricas
        categorical_cols = [c for c in ["tipo", "endereco_cidade", "endereco_bairro", "politica_cancelamento"]
                            if c in df_features.columns]

        for col in categorical_cols:
            le = LabelEncoder()
            df_features[col] = le.fit_transform(df_features[col].astype(str))
            self.label_encoders[col] = le

        return df_features

    # ------------------------------- Train -----------------------------------
    def _compute_metrics(self, y_true: np.ndarray, y_pred: np.ndarray) -> dict:
        rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
        mae = float(mean_absolute_error(y_true, y_pred))
        r2 = float(r2_score(y_true, y_pred))

        # MAPE seguro quando há valores 0 em y_true
        mask = y_true != 0
        if not np.any(mask):
            mape = float("nan")
        else:
            mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)

        return {"rmse": rmse, "mae": mae, "r2": r2, "mape": mape}

    def _scale_numeric(self, X_train: pd.DataFrame, X_test: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, list[str]]:
        numeric_cols = X_train.select_dtypes(include=[np.number]).columns.tolist()
        X_train_sc = X_train.copy()
        X_test_sc = X_test.copy()
        X_train_sc[numeric_cols] = self.scaler.fit_transform(X_train[numeric_cols])
        X_test_sc[numeric_cols] = self.scaler.transform(X_test[numeric_cols])
        return X_train_sc, X_test_sc, numeric_cols

    def _save_artifacts(self, model, features: list[str], extra_metadata: dict | None = None) -> None:
        # salvar modelo principal usado pelo serviço de recomendação
        joblib.dump(model, self.ml_dir / "price_model.joblib")
        joblib.dump(self.label_encoders, self.ml_dir / "label_encoders.pkl")
        joblib.dump(self.scaler, self.ml_dir / "scaler.pkl")

        metadata = {
            "model_type": type(model).__name__,
            "features": list(features),
            "timestamp": datetime.now().isoformat(),
        }
        if extra_metadata:
            metadata.update(extra_metadata)

        with open(self.ml_dir / "metadata.json", "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)

        logger.info(f"Modelo e artefatos salvos em {self.ml_dir}")

    def train_simple(self) -> dict:
        """Treino simples com RandomForestRegressor (sem Grid Search)."""
        latest_file = self.get_latest_etl_file()
        logger.info(f"Dados: {latest_file.name}")
        df = pd.read_csv(latest_file)
        logger.info(f"Registros: {len(df)}")

        df_features = self.prepare_features(df)
        X = df_features.drop("preco_aluguel", axis=1)
        y = df_features["preco_aluguel"].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train_sc, X_test_sc, _ = self._scale_numeric(X_train, X_test)

        logger.info("Treinando Random Forest...")
        self.model.fit(X_train_sc, y_train)

        y_pred = self.model.predict(X_test_sc)
        metrics = self._compute_metrics(y_test, y_pred)

        logger.info("=" * 70)
        logger.info("MÉTRICAS DO MODELO")
        logger.info("=" * 70)
        logger.info(f"R2:  {metrics['r2']:.4f}")
        logger.info(f"RMSE: {metrics['rmse']:.2f}")
        logger.info(f"MAE:  {metrics['mae']:.2f}")
        logger.info(f"MAPE: {metrics['mape']:.2f}%")
        logger.info("=" * 70)

        self._save_artifacts(self.model, features=X.columns.tolist(), extra_metadata={"metrics": metrics})
        return metrics

    def train_grid(self) -> dict:
        """
        Treino com Grid Search (testa múltiplas configs de RandomForest).
        Mantém estrutura similar ao bloco colado no fim do seu código.
        """
        latest_file = self.get_latest_etl_file()
        logger.info(f"Dados: {latest_file.name}")
        df = pd.read_csv(latest_file)
        logger.info(f"Registros: {len(df)}")

        df_features = self.prepare_features(df)
        X = df_features.drop("preco_aluguel", axis=1)
        y = df_features["preco_aluguel"].values

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        X_train_sc, X_test_sc, _ = self._scale_numeric(X_train, X_test)

        # Espaço de busca (ajuste conforme necessidade)
        param_grid = {
            "n_estimators": [200, 400, 600],
            "max_depth": [None, 10, 20, 30],
            "min_samples_split": [2, 5, 10],
            "min_samples_leaf": [1, 2, 4],
        }

        base_model = RandomForestRegressor(random_state=42, n_jobs=-1)
        grid_search = GridSearchCV(
            estimator=base_model,
            param_grid=param_grid,
            scoring="r2",
            cv=5,
            n_jobs=-1,
            verbose=1,
        )

        logger.info("Executando Grid Search...")
        grid_search.fit(X_train_sc, y_train)

        y_pred = grid_search.predict(X_test_sc)
        metrics = self._compute_metrics(y_test, y_pred)

        best_params = grid_search.best_params_
        best_cv_score = float(grid_search.best_score_)
        metrics.update({"best_params": best_params, "best_cv_score": best_cv_score})

        logger.info("=" * 70)
        logger.info("MELHOR MODELO (Grid Search)")
        logger.info("=" * 70)
        logger.info(f"R2:  {metrics['r2']:.4f}")
        logger.info(f"RMSE: {metrics['rmse']:.2f}")
        logger.info(f"MAE:  {metrics['mae']:.2f}")
        logger.info(f"MAPE: {metrics['mape']:.2f}%")
        logger.info(f"CV Score: {metrics['best_cv_score']:.4f}")
        logger.info(f"Parâmetros: {metrics['best_params']}")
        logger.info("=" * 70)

        # Salvar melhor modelo e metadados completos
        self.best_model = grid_search.best_estimator_
        self.best_params = best_params
        self._save_artifacts(
            self.best_model,
            features=X.columns.tolist(),
            extra_metadata={
                "best_model": {
                    "params": best_params,
                    "cv_score": best_cv_score,
                },
                "metrics": metrics,
                "training_info": {
                    "grid_search_enabled": True,
                    "cross_validation_folds": 5,
                },
            },
        )

        # Ranking simples: como só há um modelo base com múltiplos params,
        # registramos apenas a linha do melhor para manter compatibilidade.
        ranking_path = self.ml_dir / "model_ranking.txt"
        with open(ranking_path, "w", encoding="utf-8") as f:
            f.write("RANKING DE MODELOS (por R2)\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"1. RandomForestRegressor (GridSearch best): {metrics['r2']:.4f}\n")
            f.write(f"   RMSE: {metrics['rmse']:.2f}\n")
            f.write(f"   MAPE: {metrics['mape']:.2f}%\n")
            f.write(f"   Params: {best_params}\n\n")
        logger.info(f"Ranking salvo em {ranking_path}")

        return metrics


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Treinamento de modelo de preços de imóveis")
    parser.add_argument("--grid", action="store_true", help="Usa Grid Search para encontrar hiperparâmetros")
    args = parser.parse_args()

    logger.info("=" * 70)
    logger.info("TREINAMENTO DE MODELO")
    logger.info("=" * 70)

    start = datetime.now()
    try:
        trainer = ModelTrainer()
        if args.grid:
            metrics = trainer.train_grid()
        else:
            metrics = trainer.train_simple()

        elapsed = (datetime.now() - start).total_seconds()
        print("\n" + "=" * 70)
        print("TREINAMENTO CONCLUÍDO COM SUCESSO")
        print("=" * 70)
        print(f"\nTempo total: {elapsed:.1f}s ({elapsed/60:.1f} min)")
        print(f"\nResultados:")
        print(f"   R2:   {metrics['r2']:.4f}")
        print(f"   RMSE: R$ {metrics['rmse']:.2f}")
        print(f"   MAE:  R$ {metrics['mae']:.2f}")
        print(f"   MAPE: {metrics['mape']:.2f}%")
        if args.grid:
            print(f"   CV:   {metrics['best_cv_score']:.4f}")
            print("\nMelhores hiperparâmetros:")
            for k, v in metrics["best_params"].items():
                print(f"   - {k}: {v}")
        print(f"\nArquivos salvos em: {ModelTrainer().ml_dir}")
        print("\n" + "=" * 70 + "\n")

    except FileNotFoundError as e:
        print(str(e))
        sys.exit(1)
    except Exception as e:
        print(f"\nErro ao treinar modelo: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
