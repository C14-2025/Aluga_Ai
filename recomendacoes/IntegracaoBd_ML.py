import os
import sys
import pandas as pd
from pathlib import Path

# Localiza a raiz do repositório (onde está manage.py) e aponta para dados/processed
cur = Path(__file__).resolve()
repo_root = None
for p in list(cur.parents):
    if (p / 'manage.py').exists():
        repo_root = p
        break
if repo_root is None:
    repo_root = Path.cwd()

# Caminho absoluto para o dataset final em /dados/processed
DATASET_PATH = repo_root / 'dados' / 'processed' / 'dataset_final.csv'

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

