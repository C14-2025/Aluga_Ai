import os
import json

from recomendacoes.services.ml.services.data_loader import _resolve_json_path, load_raw, iter_flattened


def test_resolve_json_path():
    path = _resolve_json_path()
    assert os.path.exists(path)


def test_iter_flattened_has_expected_keys():
    items = iter_flattened()
    assert isinstance(items, list)
    if items:
        sample = items[0]
        for k in ('tipo', 'cidade', 'area_m2', 'preco_aluguel'):
            assert k in sample
