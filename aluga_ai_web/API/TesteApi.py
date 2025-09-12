import pytest
from ChamadaApi import chamada_api_status, chamada_api

def test_chamada_api_status():
    status = chamada_api_status()
    assert status == 200, f"Status retornado foi {status}, esperado 200"

def test_chamada_api_retorna_string():
    resposta = chamada_api()
    assert isinstance(resposta, str), "A resposta não é uma string."

def test_chamada_api_contem_school():
    resposta = chamada_api()
    assert "school" in resposta.lower(), "A resposta não contém o campo 'school'."
    
def test_chamada_api_nao_vazia():
    resposta = chamada_api()
    assert resposta.strip() != "", "A resposta da API está vazia."

def test_chamada_api_formato_json():
    resposta = chamada_api()
    assert resposta.strip().startswith("{"), "A resposta não está em formato JSON válido."

def test_chamada_api_status_inteiro():
    status = chamada_api_status()
    assert isinstance(status, int), "O status não é um número inteiro."