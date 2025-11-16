import os
import sys
import pandas as pd
from pathlib import Path

# Caminho absoluto para o dataset final
# Ajuste o caminho conforme necessário para o pipeline
DATASET_PATH = Path(__file__).resolve().parent.parent / 'Dados' / 'processed' / 'dataset_final.csv'

def carregar_dataset_final():
    """Carrega o dataset final processado para modelagem."""
    if not DATASET_PATH.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {DATASET_PATH}")
    df = pd.read_csv(DATASET_PATH)
    print(f"Dataset carregado de {DATASET_PATH}. Shape: {df.shape}")
    return df

if __name__ == "__main__":
    df = carregar_dataset_final()
    print(df.head())

