import pytest
from django.contrib.auth.models import User
from propriedades.models import Propriedade
from reservas.models import Reserva
from avaliacoes.models import Avaliacao
import os
import sys
import pandas as pd

@pytest.mark.django_db
def test_cria_usuario():
    user = User.objects.create_user(username='testuser', password='123456')
    assert User.objects.filter(username='testuser').exists()

@pytest.mark.django_db
def test_cria_propriedade():
    user = User.objects.create_user(username='donoteste', password='123456')
    prop = Propriedade.objects.create(owner=user, titulo='Casa Teste', descricao='...', endereco='Rua X', city='Cidade', state='Estado', preco_por_noite=100.0, ativo=True)
    assert Propriedade.objects.filter(titulo='Casa Teste').exists()
    assert prop.owner == user

@pytest.mark.django_db
def test_cria_reserva():
    user = User.objects.create_user(username='hospedeteste', password='123456')
    owner = User.objects.create_user(username='donoteste2', password='123456')
    prop = Propriedade.objects.create(owner=owner, titulo='Apto Teste', descricao='...', endereco='Rua Y', city='Cidade', state='Estado', preco_por_noite=200.0, ativo=True)
    reserva = Reserva.objects.create(guest=user, propriedade=prop, inicio='2025-10-01', fim='2025-10-10', status=Reserva.STATUS_CONFIRMED)
    assert Reserva.objects.filter(propriedade=prop, guest=user).exists()
    assert reserva.status == Reserva.STATUS_CONFIRMED

@pytest.mark.django_db
def test_cria_avaliacao():
    user = User.objects.create_user(username='autoravaliacao', password='123456')
    owner = User.objects.create_user(username='donoteste3', password='123456')
    prop = Propriedade.objects.create(owner=owner, titulo='Casa Avaliada', descricao='...', endereco='Rua Z', city='Cidade', state='Estado', preco_por_noite=150.0, ativo=True)
    avaliacao = Avaliacao.objects.create(autor=user, propriedade=prop, nota=4, comentario='Muito bom!')
    assert Avaliacao.objects.filter(propriedade=prop, autor=user).exists()
    assert avaliacao.nota == 4

@pytest.mark.django_db
def test_importar_propriedades_csv(tmp_path):
    from Dados.IntegracaoBd import importar_propriedades_csv
    # Cria CSV temporário
    csv_path = tmp_path / 'test_props.csv'
    df = pd.DataFrame({
        'quartos': [2], 'banheiros': [1], 'vagas_garagem': [1], 'area_m2': [50], 'nota_media': [4.5],
        'camas': [2], 'condominio': [300], 'iptu': [50], 'max_hospedes': [4], 'tempo_anuncio_meses': [12],
        'latitude': [-23.5], 'longitude': [-46.6], 'disp_alta_demanda': [False], 'num_comodidades': [2],
        'num_avaliacoes': [1], 'num_fotos': [2], 'anfitriao_superhost': [1], 'disp_preco_aluguel_log': [5.3],
        'disp_preco_aluguel': [200], 'status_inativo': [False]
    })
    df.to_csv(csv_path, index=False)
    importar_propriedades_csv(str(csv_path))
    assert Propriedade.objects.filter(titulo='Propriedade CSV').exists()
