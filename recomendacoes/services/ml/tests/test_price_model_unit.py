import os
import pytest

try:
    from recomendacoes.services.ml.services.model import PriceModel
except Exception:
    PriceModel = None


def setup_module(module):
    os.environ['ALUGAAI_DADOS_JSON'] = 'aluga_ai_web/Dados/raw/imoveis_gerados.json'


def test_price_model_instance_available():
    if PriceModel is None:
        pytest.skip("PriceModel não disponível para teste")
    model = PriceModel.instance()
    assert model is not None


def test_price_model_predict_positive():
    if PriceModel is None:
        pytest.skip("PriceModel não disponível para teste")

    model = PriceModel.instance()
    test_features = {
        'tipo': 'apartment',
        'cidade': 'Sao Paulo',
        'area_m2': 60.0,
        'quartos': 2,
        'banheiros': 1,
        'vagas_garagem': 1,
        'condominio': 300.0,
        'iptu': 200.0
    }

    price, method, details = model.predict(test_features, return_details=True)
    assert price > 0
    assert isinstance(method, str)
