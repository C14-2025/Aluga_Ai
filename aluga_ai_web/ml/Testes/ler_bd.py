import pytest
import pandas as pd
from pathlib import Path
import sys

# Garante que o diretório ml/ está no sys.path para importação
import os
ML_PATH = Path(__file__).resolve().parent.parent
if str(ML_PATH) not in sys.path:
    sys.path.insert(0, str(ML_PATH))


# Importação robusta para pytest (importa o módulo .py como pacote)
import importlib.util
import pathlib
ml_dir = Path(__file__).resolve().parent.parent
ml_file = ml_dir / 'IntegracaoBd-ML.py'
spec = importlib.util.spec_from_file_location('IntegracaoBd_ML', ml_file)
integracao = importlib.util.module_from_spec(spec)
spec.loader.exec_module(integracao)

def test_carregar_dataset_final_existente(tmp_path, monkeypatch):
    # Cria um CSV temporário simulando o dataset final
    df = pd.DataFrame({
        'col1': [1, 2],
        'col2': [3, 4]
    })
    fake_path = tmp_path / 'dataset_final.csv'
    df.to_csv(fake_path, index=False)
    monkeypatch.setattr(integracao, 'DATASET_PATH', fake_path)
    df_loaded = integracao.carregar_dataset_final()
    assert not df_loaded.empty
    assert list(df_loaded.columns) == ['col1', 'col2']
    assert df_loaded.shape == (2, 2)

def test_carregar_dataset_final_inexistente(tmp_path, monkeypatch):
    fake_path = tmp_path / 'dataset_final.csv'
    monkeypatch.setattr(integracao, 'DATASET_PATH', fake_path)
    with pytest.raises(FileNotFoundError):
        integracao.carregar_dataset_final()
