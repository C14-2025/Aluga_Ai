import os
import pytest

from jobs import validate_recommendation_system as vrs


def setup_module(module):
    # garantir que o caminho para os dados está configurado para os testes
    os.environ['ALUGAAI_DADOS_JSON'] = 'aluga_ai_web/Dados/raw/imoveis_gerados.json'


def test_required_files_exist():
    assert vrs.test_required_files() is True


def test_model_loading():
    assert vrs.test_model_loading() is True


def test_price_prediction():
    assert vrs.test_price_prediction() is True


def test_recommendation_system():
    assert vrs.test_recommendation_system() is True
