#!/usr/bin/env python
"""
Script para popular o banco de dados com dados de exemplo
Execute com: python manage.py shell < populate_data.py
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aluga_ai_web.settings')
django.setup()

from django.contrib.auth.models import User
from reservas.models import Imovel, Reserva, Avaliacao

def criar_usuarios():
    """Criar usuários de exemplo"""
    usuarios = []
    
    # Criar anfitriões
    anfitrioes = [
        {'username': 'joao_silva', 'email': 'joao@example.com', 'first_name': 'João', 'last_name': 'Silva'},
        {'username': 'maria_santos', 'email': 'maria@example.com', 'first_name': 'Maria', 'last_name': 'Santos'},
        {'username': 'pedro_oliveira', 'email': 'pedro@example.com', 'first_name': 'Pedro', 'last_name': 'Oliveira'},
        {'username': 'ana_costa', 'email': 'ana@example.com', 'first_name': 'Ana', 'last_name': 'Costa'},
        {'username': 'carlos_lima', 'email': 'carlos@example.com', 'first_name': 'Carlos', 'last_name': 'Lima'},
    ]
    
    for dados in anfitrioes:
        user, created = User.objects.get_or_create(
            username=dados['username'],
            defaults={
                'email': dados['email'],
                'first_name': dados['first_name'],
                'last_name': dados['last_name']
            }
        )
        if created:
            user.set_password('123456')
            user.save()
        usuarios.append(user)
    
    # Criar hóspedes
    hospedes = [
        {'username': 'lucas_ferreira', 'email': 'lucas@example.com', 'first_name': 'Lucas', 'last_name': 'Ferreira'},
        {'username': 'juliana_ribeiro', 'email': 'juliana@example.com', 'first_name': 'Juliana', 'last_name': 'Ribeiro'},
        {'username': 'rafael_mendes', 'email': 'rafael@example.com', 'first_name': 'Rafael', 'last_name': 'Mendes'},
        {'username': 'camila_alves', 'email': 'camila@example.com', 'first_name': 'Camila', 'last_name': 'Alves'},
    ]
    
    for dados in hospedes:
        user, created = User.objects.get_or_create(
            username=dados['username'],
            defaults={
                'email': dados['email'],
                'first_name': dados['first_name'],
                'last_name': dados['last_name']
            }
        )
        if created:
            user.set_password('123456')
            user.save()
        usuarios.append(user)
    
    return usuarios

def criar_imoveis(anfitrioes):
    """Criar imóveis de exemplo"""
    imoveis = []
    
    dados_imoveis = [
        {
            'tipo': 'apartamento',
            'cidade': 'São Paulo',
            'bairro': 'Centro',
            'rua': 'Rua das Flores',
            'numero': '123',
            'cep': '01234-567',
            'complemento': 'Apto 101',
            'latitude': -23.5505,
            'longitude': -46.6333,
            'quartos': 2,
            'banheiros': 1,
            'vagas_garagem': 1,
            'area_m2': 60,
            'andar': 5,
            'ano_construcao': 2020,
            'preco_aluguel': Decimal('1500.00'),
            'condominio': Decimal('200.00'),
            'iptu': Decimal('100.00'),
            'descricao': 'Apartamento aconchegante no centro da cidade',
            'comodidades': ['Wi-Fi', 'Ar-condicionado', 'Cozinha', 'TV'],
            'regras_casa': ['Proibido fumar', 'Não permite festas'],
            'tags': ['Pet friendly', 'Próximo ao metrô'],
            'mobiliado': True,
            'aceita_pets': True,
            'max_hospedes': 4,
            'camas': 2,
            'tipo_cama': 'Casal',
            'politica_cancelamento': 'moderada',
            'anfitriao_superhost': True
        },
        {
            'tipo': 'casa',
            'cidade': 'Rio de Janeiro',
            'bairro': 'Copacabana',
            'rua': 'Avenida Atlântica',
            'numero': '456',
            'cep': '22070-000',
            'complemento': '',
            'latitude': -22.9068,
            'longitude': -43.1729,
            'quartos': 3,
            'banheiros': 2,
            'vagas_garagem': 2,
            'area_m2': 120,
            'andar': 0,
            'ano_construcao': 2018,
            'preco_aluguel': Decimal('2500.00'),
            'condominio': Decimal('0.00'),
            'iptu': Decimal('300.00'),
            'descricao': 'Casa com vista para o mar',
            'comodidades': ['Wi-Fi', 'Piscina', 'Churrasqueira', 'Estacionamento'],
            'regras_casa': ['Silêncio após 22h', 'Check-in após 14h'],
            'tags': ['Vista para o mar', 'Ideal para famílias'],
            'mobiliado': True,
            'aceita_pets': True,
            'max_hospedes': 6,
            'camas': 3,
            'tipo_cama': 'King',
            'politica_cancelamento': 'flexível',
            'anfitriao_superhost': True
        },
        {
            'tipo': 'studio',
            'cidade': 'Belo Horizonte',
            'bairro': 'Savassi',
            'rua': 'Rua Pernambuco',
            'numero': '789',
            'cep': '30112-000',
            'complemento': 'Studio 15',
            'latitude': -19.9167,
            'longitude': -43.9345,
            'quartos': 1,
            'banheiros': 1,
            'vagas_garagem': 0,
            'area_m2': 35,
            'andar': 8,
            'ano_construcao': 2021,
            'preco_aluguel': Decimal('800.00'),
            'condominio': Decimal('150.00'),
            'iptu': Decimal('50.00'),
            'descricao': 'Studio moderno e funcional',
            'comodidades': ['Wi-Fi', 'Ar-condicionado', 'Cozinha compacta'],
            'regras_casa': ['Proibido fumar', 'Máximo 2 hóspedes'],
            'tags': ['Moderno', 'Próximo ao centro'],
            'mobiliado': True,
            'aceita_pets': False,
            'max_hospedes': 2,
            'camas': 1,
            'tipo_cama': 'Solteiro',
            'politica_cancelamento': 'rigorosa',
            'anfitriao_superhost': False
        },
        {
            'tipo': 'loft',
            'cidade': 'São Paulo',
            'bairro': 'Vila Madalena',
            'rua': 'Rua Harmonia',
            'numero': '321',
            'cep': '05435-000',
            'complemento': 'Loft 2',
            'latitude': -23.5505,
            'longitude': -46.6333,
            'quartos': 1,
            'banheiros': 1,
            'vagas_garagem': 1,
            'area_m2': 80,
            'andar': 3,
            'ano_construcao': 2019,
            'preco_aluguel': Decimal('1800.00'),
            'condominio': Decimal('250.00'),
            'iptu': Decimal('120.00'),
            'descricao': 'Loft industrial com design moderno',
            'comodidades': ['Wi-Fi', 'Ar-condicionado', 'Cozinha gourmet', 'Varanda'],
            'regras_casa': ['Proibido fumar', 'Não permite festas'],
            'tags': ['Design moderno', 'Bairro boêmio'],
            'mobiliado': True,
            'aceita_pets': True,
            'max_hospedes': 3,
            'camas': 1,
            'tipo_cama': 'Queen',
            'politica_cancelamento': 'moderada',
            'anfitriao_superhost': True
        },
        {
            'tipo': 'apartamento',
            'cidade': 'Curitiba',
            'bairro': 'Centro',
            'rua': 'Rua XV de Novembro',
            'numero': '654',
            'cep': '80020-000',
            'complemento': 'Apto 302',
            'latitude': -25.4284,
            'longitude': -49.2733,
            'quartos': 2,
            'banheiros': 2,
            'vagas_garagem': 1,
            'area_m2': 75,
            'andar': 3,
            'ano_construcao': 2017,
            'preco_aluguel': Decimal('1200.00'),
            'condominio': Decimal('180.00'),
            'iptu': Decimal('80.00'),
            'descricao': 'Apartamento confortável no centro histórico',
            'comodidades': ['Wi-Fi', 'Ar-condicionado', 'Cozinha', 'TV', 'Elevador'],
            'regras_casa': ['Silêncio após 22h', 'Check-in após 14h'],
            'tags': ['Centro histórico', 'Acessível'],
            'mobiliado': False,
            'aceita_pets': False,
            'max_hospedes': 4,
            'camas': 2,
            'tipo_cama': 'Casal',
            'politica_cancelamento': 'moderada',
            'anfitriao_superhost': False
        }
    ]
    
    for i, dados in enumerate(dados_imoveis):
        anfitriao = anfitrioes[i % len(anfitrioes)]
        
        imovel = Imovel.objects.create(
            tipo=dados['tipo'],
            cidade=dados['cidade'],
            bairro=dados['bairro'],
            rua=dados['rua'],
            numero=dados['numero'],
            cep=dados['cep'],
            complemento=dados['complemento'],
            latitude=dados['latitude'],
            longitude=dados['longitude'],
            quartos=dados['quartos'],
            banheiros=dados['banheiros'],
            vagas_garagem=dados['vagas_garagem'],
            area_m2=dados['area_m2'],
            andar=dados['andar'],
            ano_construcao=dados['ano_construcao'],
            preco_aluguel=dados['preco_aluguel'],
            condominio=dados['condominio'],
            iptu=dados['iptu'],
            descricao=dados['descricao'],
            comodidades=dados['comodidades'],
            regras_casa=dados['regras_casa'],
            tags=dados['tags'],
            mobiliado=dados['mobiliado'],
            aceita_pets=dados['aceita_pets'],
            max_hospedes=dados['max_hospedes'],
            camas=dados['camas'],
            tipo_cama=dados['tipo_cama'],
            politica_cancelamento=dados['politica_cancelamento'],
            anfitriao=anfitriao,
            anfitriao_nome=f"{anfitriao.first_name} {anfitriao.last_name}",
            anfitriao_superhost=dados['anfitriao_superhost'],
            tempo_anuncio_meses=random.randint(1, 12)
        )
        imoveis.append(imovel)
    
    return imoveis

def criar_reservas(imoveis, usuarios):
    """Criar reservas de exemplo"""
    reservas = []
    
    # Criar algumas reservas passadas (concluídas)
    for i in range(3):
        imovel = random.choice(imoveis)
        hospede = random.choice([u for u in usuarios if u not in [imovel.anfitriao]])
        
        data_checkin = date.today() - timedelta(days=random.randint(30, 90))
        data_checkout = data_checkin + timedelta(days=random.randint(2, 7))
        
        numero_noites = (data_checkout - data_checkin).days
        preco_por_noite = imovel.preco_aluguel
        preco_base = preco_por_noite * numero_noites
        taxa_servico = preco_base * Decimal('0.10')
        taxa_limpeza = Decimal('50.00')
        desconto = preco_base * Decimal('0.05') if numero_noites >= 7 else Decimal('0.00')
        preco_total = preco_base + taxa_servico + taxa_limpeza - desconto
        
        reserva = Reserva.objects.create(
            imovel=imovel,
            hospede=hospede,
            data_checkin=data_checkin,
            data_checkout=data_checkout,
            numero_hospedes=random.randint(1, imovel.max_hospedes),
            preco_total=preco_total,
            preco_por_noite=preco_por_noite,
            numero_noites=numero_noites,
            taxa_limpeza=taxa_limpeza,
            taxa_servico=taxa_servico,
            desconto=desconto,
            status='concluida',
            observacoes=f'Reserva de exemplo {i+1}'
        )
        reservas.append(reserva)
    
    # Criar algumas reservas futuras
    for i in range(5):
        imovel = random.choice(imoveis)
        hospede = random.choice([u for u in usuarios if u not in [imovel.anfitriao]])
        
        data_checkin = date.today() + timedelta(days=random.randint(7, 30))
        data_checkout = data_checkin + timedelta(days=random.randint(2, 5))
        
        numero_noites = (data_checkout - data_checkin).days
        preco_por_noite = imovel.preco_aluguel
        preco_base = preco_por_noite * numero_noites
        taxa_servico = preco_base * Decimal('0.10')
        taxa_limpeza = Decimal('50.00')
        desconto = preco_base * Decimal('0.05') if numero_noites >= 7 else Decimal('0.00')
        preco_total = preco_base + taxa_servico + taxa_limpeza - desconto
        
        status_options = ['pendente', 'confirmada']
        status = random.choice(status_options)
        
        reserva = Reserva.objects.create(
            imovel=imovel,
            hospede=hospede,
            data_checkin=data_checkin,
            data_checkout=data_checkout,
            numero_hospedes=random.randint(1, imovel.max_hospedes),
            preco_total=preco_total,
            preco_por_noite=preco_por_noite,
            numero_noites=numero_noites,
            taxa_limpeza=taxa_limpeza,
            taxa_servico=taxa_servico,
            desconto=desconto,
            status=status,
            observacoes=f'Reserva futura {i+1}'
        )
        reservas.append(reserva)
    
    return reservas

def criar_avaliacoes(reservas):
    """Criar avaliações de exemplo"""
    avaliacoes = []
    
    # Criar avaliações para reservas concluídas
    reservas_concluidas = [r for r in reservas if r.status == 'concluida']
    
    for reserva in reservas_concluidas:
        nota = random.randint(3, 5)
        comentarios = [
            'Excelente estadia!',
            'Muito bom, recomendo!',
            'Apartamento limpo e confortável.',
            'Anfitrião muito atencioso.',
            'Localização excelente!',
            'Tive alguns problemas, mas foram resolvidos.',
            'Boa estadia, voltaria novamente.'
        ]
        
        avaliacao = Avaliacao.objects.create(
            reserva=reserva,
            nota=nota,
            comentario=random.choice(comentarios),
            limpeza=random.randint(3, 5),
            comunicacao=random.randint(3, 5),
            localizacao=random.randint(3, 5),
            valor=random.randint(3, 5)
        )
        avaliacoes.append(avaliacao)
        
        # Atualizar nota média do imóvel
        imovel = reserva.imovel
        avaliacoes_imovel = Avaliacao.objects.filter(reserva__imovel=imovel)
        if avaliacoes_imovel.exists():
            nota_media = sum(a.nota for a in avaliacoes_imovel) / avaliacoes_imovel.count()
            imovel.nota_media = round(nota_media, 2)
            imovel.total_avaliacoes = avaliacoes_imovel.count()
            imovel.save()
    
    return avaliacoes

def main():
    """Função principal para popular o banco"""
    print("Criando usuários...")
    usuarios = criar_usuarios()
    print(f"Criados {len(usuarios)} usuários")
    
    print("Criando imóveis...")
    anfitrioes = usuarios[:5]  # Primeiros 5 são anfitriões
    imoveis = criar_imoveis(anfitrioes)
    print(f"Criados {len(imoveis)} imóveis")
    
    print("Criando reservas...")
    reservas = criar_reservas(imoveis, usuarios)
    print(f"Criadas {len(reservas)} reservas")
    
    print("Criando avaliações...")
    avaliacoes = criar_avaliacoes(reservas)
    print(f"Criadas {len(avaliacoes)} avaliações")
    
    print("\nDados populados com sucesso!")
    print(f"Total de usuários: {User.objects.count()}")
    print(f"Total de imóveis: {Imovel.objects.count()}")
    print(f"Total de reservas: {Reserva.objects.count()}")
    print(f"Total de avaliações: {Avaliacao.objects.count()}")

if __name__ == '__main__':
    main()
