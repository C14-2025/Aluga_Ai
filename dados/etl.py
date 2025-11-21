import json
import logging
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------------
# ETL
# -----------------------------------------------------------------------------
class ETLPipeline:
    """Pipeline ETL para processar dados de imóveis."""

    def __init__(self):
        root = Path(__file__).resolve().parent
        self.raw_dir = root / "raw"
        self.processed_dir = root / "processed"
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def extract(self) -> pd.DataFrame:
        """Extrai dados do arquivo JSON."""
        json_file = self.raw_dir / "imoveis_gerados.json"
        
        if not json_file.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {json_file}")
        
        logger.info(f"Carregando dados de {json_file}")
        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        df = pd.DataFrame(data)
        logger.info(f"Registros extraídos: {len(df)}")
        return df

    def transform(self, df: pd.DataFrame) -> pd.DataFrame:
        """Transforma e enriquece os dados."""
        logger.info("Iniciando transformações...")
        
        # Expandir coluna endereco
        endereco_df = pd.json_normalize(df["endereco"])
        endereco_df.columns = ["endereco_" + col for col in endereco_df.columns]
        df = pd.concat([df.drop("endereco", axis=1), endereco_df], axis=1)
        
        # Expandir coluna anfitriao
        anfitriao_df = pd.json_normalize(df["anfitriao"])
        anfitriao_df.columns = ["anfitriao_" + col for col in anfitriao_df.columns]
        df = pd.concat([df.drop("anfitriao", axis=1), anfitriao_df], axis=1)
        
        # Features derivadas de listas
        df["num_comodidades"] = df["comodidades"].apply(lambda x: len(x) if isinstance(x, list) else 0)
        df["num_fotos"] = df["fotos"].apply(lambda x: len(x) if isinstance(x, list) else 0)
        df["num_avaliacoes"] = df["avaliacoes"].apply(lambda x: len(x) if isinstance(x, list) else 0)
        df["num_regras"] = df["regras_casa"].apply(lambda x: len(x) if isinstance(x, list) else 0)
        df["num_tags"] = df["tags"].apply(lambda x: len(x) if isinstance(x, list) else 0)
        
        # Feature de localização estratégica
        df["loc_estrategica"] = (
            (df["distancia_metro_km"] < 1.0) | (df["distancia_onibus_km"] < 0.5)
        ).astype(int)
        
        # Quality score baseado em múltiplos fatores
        df["quality_score"] = (
            df["nota_media"] * 0.4 +
            (df["num_avaliacoes"] / df["num_avaliacoes"].max()) * 2 +
            (df["num_fotos"] / 10) * 0.5 +
            df["anfitriao_superhost"].astype(int) * 1.0
        )
        
        # Remover colunas complexas que não serão usadas no modelo
        cols_to_drop = ["comodidades", "fotos", "avaliacoes", "regras_casa", 
                        "tags", "disponibilidade", "descricao", "endereco_complemento",
                        "endereco_cep", "endereco_rua", "endereco_numero",
                        "anfitriao_nome", "anfitriao_foto", "checkin", "checkout"]
        df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])
        
        # Tratar valores ausentes
        df = df.fillna(0)
        
        # Filtrar outliers extremos (opcional)
        q99 = df["preco_aluguel"].quantile(0.99)
        q01 = df["preco_aluguel"].quantile(0.01)
        df = df[(df["preco_aluguel"] >= q01) & (df["preco_aluguel"] <= q99)]
        
        logger.info(f"Transformações concluídas. Registros finais: {len(df)}")
        return df

    def load(self, df: pd.DataFrame) -> Path:
        """Salva dados processados."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.processed_dir / f"imoveis_processed_{timestamp}.csv"
        
        df.to_csv(output_file, index=False, encoding="utf-8")
        logger.info(f"Dados salvos em: {output_file}")
        return output_file

    def run(self) -> Path:
        """Executa pipeline completo."""
        logger.info("=" * 70)
        logger.info("INICIANDO PIPELINE ETL")
        logger.info("=" * 70)
        
        try:
            # Extract
            df_raw = self.extract()
            
            # Transform
            df_processed = self.transform(df_raw)
            
            # Load
            output_path = self.load(df_processed)
            
            logger.info("=" * 70)
            logger.info("ETL CONCLUÍDO COM SUCESSO")
            logger.info("=" * 70)
            logger.info(f"Arquivo final: {output_path}")
            logger.info(f"Registros processados: {len(df_processed)}")
            logger.info(f"Colunas: {len(df_processed.columns)}")
            
            return output_path
            
        except Exception as e:
            logger.error(f"Erro no pipeline ETL: {e}")
            raise


# -----------------------------------------------------------------------------
# CLI
# -----------------------------------------------------------------------------
def main():
    try:
        pipeline = ETLPipeline()
        pipeline.run()
        sys.exit(0)
    except Exception as e:
        logger.error(f"Falha na execução: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
