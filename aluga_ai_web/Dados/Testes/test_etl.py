
import os
import json
import pytest
import sys
import pathlib

# Importação robusta do ConstrucaoDeDados
try:
    import ConstrucaoDeDados as cd
except ImportError:
    # Tenta importar do diretório pai (Dados)
    base_dir = pathlib.Path(__file__).resolve().parent.parent
    if str(base_dir) not in sys.path:
        sys.path.insert(0, str(base_dir))
    import ConstrucaoDeDados as cd

from ConstrucaoDeDados import gerar_imovel

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


def test_gerar_imovel_retorna_dict():
    imovel = gerar_imovel()
    assert isinstance(imovel, dict)
    assert "tipo" in imovel
    assert "preco_aluguel" in imovel


# Testes removidos: test_obter_dados_tabela_retorna_lista, test_view_listar_imoveis, test_view_listar_imoveis_sem_dados

def test_preco_m2_por_bairro():
    valor = cd.preco_m2_por_bairro("São Paulo", "Centro")
    assert valor == 45

    valor_random = cd.preco_m2_por_bairro("CidadeInexistente", "BairroFake")
    assert 20 <= valor_random <= 60


def test_gerar_disponibilidade_formatos():
    disponibilidade = cd.gerar_disponibilidade()
    assert isinstance(disponibilidade, list)
    for periodo in disponibilidade:
        assert "inicio" in periodo and "fim" in periodo
        assert len(periodo["inicio"]) == 10
        assert len(periodo["fim"]) == 10
        assert periodo["inicio"] <= periodo["fim"]


def test_gerar_lista_imoveis_zero():
    lista = cd.gerar_lista_imoveis(0)
    assert isinstance(lista, list)
    assert len(lista) == 0


#verifica formato e range de check-in e check-out
def test_checkin_checkout_format():
    imovel = cd.gerar_imovel()
    checkin = imovel["checkin"]
    checkout = imovel["checkout"]
    # Deve estar no formato HH:00
    assert checkin.endswith(":00")
    assert checkout.endswith(":00")
    # Check-in entre 13h e 16h, checkout entre 10h e 12h
    assert 13 <= int(checkin.split(":")[0]) <= 16
    assert 10 <= int(checkout.split(":")[0]) <= 12

#verifica formato do cep
def test_endereco_cep_format():
    imovel = cd.gerar_imovel()
    cep = imovel["endereco"]["cep"]
    # Formato deve ser 5 dígitos + hífen + 3 dígitos
    assert len(cep) == 9
    parte1, parte2 = cep.split("-")
    assert parte1.isdigit() and len(parte1) == 5
    assert parte2.isdigit() and len(parte2) == 3

#verifica se max_hospedes está coerente com o número de quartos
def test_max_hospedes_relacao_quartos():
    imovel = cd.gerar_imovel()
    quartos = imovel["quartos"]
    max_hospedes = imovel["max_hospedes"]
    # Regra de geração: max_hospedes entre n_quartos e 2*n_quartos+2
    assert quartos <= max_hospedes <= (quartos * 2 + 2)


#Com o mock, só será gerado 1 bloco de disponibilidade.
#Esse bloco sempre começa em 10 dias a partir de hoje e dura 5 dias.
#Verificamos que "inicio" e "fim" estão presentes e em ordem correta.

def test_gerar_disponibilidade_com_mock(monkeypatch):
    # Mocka random.randint para controlar os valores
    chamadas = {"count": 0}

    def fake_randint(a, b):
        chamadas["count"] += 1
        # 1ª chamada -> quantidade de blocos
        if chamadas["count"] == 1:
            return 1
        # 2ª chamada -> dias para início
        elif chamadas["count"] == 2:
            return 10
        # 3ª chamada -> dias para duração
        elif chamadas["count"] == 3:
            return 5
        return a  # fallback seguro

    monkeypatch.setattr(cd.random, "randint", fake_randint)

    disponibilidade = cd.gerar_disponibilidade()
    assert isinstance(disponibilidade, list)
    assert len(disponibilidade) == 1

    periodo = disponibilidade[0]
    assert "inicio" in periodo and "fim" in periodo
    assert periodo["inicio"] <= periodo["fim"]
    # Busca um imóvel para validar a regra de max_hospedes/quartos
    imovel = cd.gerar_imovel()
    quartos = imovel["quartos"]
    max_hospedes = imovel["max_hospedes"]
    assert quartos <= max_hospedes <= (quartos * 2 + 2)


#Com o mock, só será gerado 1 bloco de disponibilidade.
#Esse bloco sempre começa em 10 dias a partir de hoje e dura 5 dias.
#Verificamos que "inicio" e "fim" estão presentes e em ordem correta.

def test_gerar_disponibilidade_com_mock(monkeypatch):
    # Mocka random.randint para controlar os valores
    chamadas = {"count": 0}

    def fake_randint(a, b):
        chamadas["count"] += 1
        # 1ª chamada -> quantidade de blocos
        if chamadas["count"] == 1:
            return 1
        # 2ª chamada -> dias para início
        elif chamadas["count"] == 2:
            return 10
        # 3ª chamada -> dias para duração
        elif chamadas["count"] == 3:
            return 5
        return a  # fallback seguro

    monkeypatch.setattr(cd.random, "randint", fake_randint)

    disponibilidade = cd.gerar_disponibilidade()
    assert isinstance(disponibilidade, list)
    assert len(disponibilidade) == 1

    periodo = disponibilidade[0]
    assert "inicio" in periodo and "fim" in periodo
    assert periodo["inicio"] <= periodo["fim"]

