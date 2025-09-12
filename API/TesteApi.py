import pytest
from ChamadaApi import chamada_api_status

def test_chamada_api_status():
    status = chamada_api_status()
    assert status == 200, f"Status retornado foi {status}, esperado 200"
    