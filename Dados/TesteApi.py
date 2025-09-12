import os
import json
import pytest
import sys
import pathlib

try:
    import ConstrucaoDeDados as cd
except ModuleNotFoundError:
    sys.path.append(str(pathlib.Path(__file__).parent))
    import ConstrucaoDeDados as cd

CAMPOS_OBRIGATORIOS = {
    "tipo", "endereco", "quartos", "banheiros", "vagas_garagem", "area_m2",
    "preco_aluguel", "descricao", "comodidades", "fotos", "avaliacoes",
    "nota_media", "regras_casa", "camas", "tipo_cama", "politica_cancelamento",
    "anfitriao", "wifi", "checkin", "checkout", "ano_construcao", "andar",
    "condominio", "iptu", "mobiliado", "distancia_metro_km",
    "distancia_onibus_km", "max_hospedes", "tempo_anuncio_meses", "status",
    "latitude", "longitude", "tags", "disponibilidade"
}

def test_gerar_lista_tamanho():
    n = 15
    lista = cd.gerar_lista_imoveis(n)
    assert isinstance(lista, list)
    assert len(lista) == n

def test_campos_obrigatorios():
    imovel = cd.gerar_imovel()
    faltando = CAMPOS_OBRIGATORIOS - set(imovel.keys())
    assert not faltando, f"Campos faltando: {faltando}"

def test_valores_intervalos():
    imovel = cd.gerar_imovel()
    assert imovel["preco_aluguel"] > 0
    assert 0 <= imovel["nota_media"] <= 5
    assert imovel["quartos"] >= 1
    assert imovel["banheiros"] >= 1
    if imovel["tipo"] == "Apartamento":
        assert 30 <= imovel["area_m2"] <= 300
        assert imovel["andar"] >= 0
    else:
        assert 50 <= imovel["area_m2"] <= 500
        assert imovel["andar"] == 0
    assert -35 < imovel["latitude"] < 5
    assert -75 < imovel["longitude"] < -30

def test_endereco_estrutura():
    imovel = cd.gerar_imovel()
    end = imovel["endereco"]
    for k in ["cidade", "bairro", "rua", "numero", "cep"]:
        assert k in end

def test_avaliacoes_formato():
    imovel = cd.gerar_imovel()
    avals = imovel["avaliacoes"]
    assert isinstance(avals, list)
    if avals:
        a = avals[0]
        for k in ["nota", "comentario", "data", "hospede"]:
            assert k in a

def test_gera_arquivo_json(tmp_path):
    # gera 5 imóveis e salva manualmente simulando main
    imoveis = cd.gerar_lista_imoveis(5)
    destino = tmp_path / "imoveis_test.json"
    with open(destino, "w", encoding="utf-8") as f:
        json.dump(imoveis, f, ensure_ascii=False, indent=2)
    assert destino.exists()
    with open(destino, "r", encoding="utf-8") as f:
        dados = json.load(f)
    assert isinstance(dados, list) and len(dados) == 5

def test_tags_e_comodidades():
    imovel = cd.gerar_imovel()
    assert isinstance(imovel["tags"], list)
    assert 1 <= len(imovel["tags"]) <= 4
    assert isinstance(imovel["comodidades"], list)
    assert 4 <= len(imovel["comodidades"]) <= 8

def test_disponibilidade_periodos_validos():
    imovel = cd.gerar_imovel()
    for periodo in imovel["disponibilidade"]:
        assert "inicio" in periodo and "fim" in periodo
        assert periodo["inicio"] <= periodo["fim"]
