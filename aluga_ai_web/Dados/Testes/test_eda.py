
import pytest
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Adiciona o diretório do eda.py ao sys.path para importação
EDA_PATH = Path(__file__).resolve().parent.parent
if str(EDA_PATH) not in sys.path:
	sys.path.insert(0, str(EDA_PATH))

import eda

def get_sample_data():
	# Pequeno exemplo de dados simulando o JSON processado
	return [
		{
			"endereco": {"cidade": "São Paulo", "bairro": "Centro", "rua": "Rua A", "numero": 1},
			"quartos": 2,
			"banheiros": 1,
			"vagas_garagem": 1,
			"area_m2": 50,
			"nota_media": 4.5,
			"camas": 2,
			"condominio": 300,
			"iptu": 50,
			"max_hospedes": 4,
			"tempo_anuncio_meses": 12,
			"latitude": -23.5,
			"longitude": -46.6,
			"disponibilidade": [{"preco_aluguel": 200, "alta_demanda": False}],
			"comodidades": ["Wi-Fi", "Ar"],
			"avaliacoes": [{"nota": 5}],
			"fotos": ["url1", "url2"],
			"anfitriao": {"nome": "João", "superhost": True},
			"tipo": "Apartamento",
			"politica_cancelamento": "Flexível",
			"tipo_cama": "Casal",
			"status": "ativo"
		}
	]

def test_carregar_dados(tmp_path, monkeypatch):
	# Cria um arquivo JSON temporário
	data = get_sample_data()
	file_path = tmp_path / "imoveis_gerados.json"
	with open(file_path, "w", encoding="utf-8") as f:
		import json
		json.dump(data, f)

	monkeypatch.setattr(eda, "RAW_PATH", file_path)
	df = eda.carregar_dados()
	assert not df.empty
	assert "endereco.cidade" in df.columns or "endereco_cidade" in df.columns

def test_limpar_colunas_features():
	df = pd.json_normalize(get_sample_data())
	eda_obj = eda.Eda(df)
	eda_obj.limpar_colunas_features()
	df2 = eda_obj.df
	assert "endereco_cidade" in df2.columns
	assert "num_comodidades" in df2.columns
	assert "num_avaliacoes" in df2.columns
	assert "num_fotos" in df2.columns
	assert "anfitriao_superhost" in df2.columns
	assert df2["anfitriao_superhost"].iloc[0] == 1

def test_explodir_disponibilidade():
	df = pd.json_normalize(get_sample_data())
	eda_obj = eda.Eda(df)
	eda_obj.limpar_colunas_features()
	eda_obj.explodir_disponibilidade()
	df2 = eda_obj.df
	assert "disp_preco_aluguel" in df2.columns
	assert df2.shape[0] == 1

def test_preparar_dados():
	df = pd.json_normalize(get_sample_data())
	eda_obj = eda.Eda(df)
	eda_obj.preparar_dados()
	df2 = eda_obj.df
	assert "disp_preco_aluguel" in df2.columns
	assert "num_comodidades" in df2.columns

def test_processar_para_modelagem(tmp_path):
	df = pd.json_normalize(get_sample_data())
	eda_obj = eda.Eda(df)
	eda_obj.preparar_dados()
	# Salvar CSV em pasta temporária
	out_csv = tmp_path / "dataset_final.csv"
	df_model = eda_obj.processar_para_modelagem(salvar_csv=True)
	# O arquivo deve ser criado
	assert out_csv.exists() or Path("processed/dataset_final.csv").exists()
	# Deve conter a coluna log-transformada
	assert "disp_preco_aluguel_log" in df_model.columns
	# Não deve haver NaN
	assert not df_model.isnull().any().any()
