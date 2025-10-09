#!/usr/bin/env python
"""
Script simples para criar dados de exemplo
Execute com: python create_sample_data.py
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

def main():
    print("Criando dados de exemplo...")
    
    # Criar usuários
    print("1. Criando usuários...")
    
    # Anfitrião
    anfitriao, created = User.objects.get_or_create(
        username='anfitriao',
        defaults={
            'email': 'anfitriao@example.com',
            'first_name': 'João',
            'last_name': 'Silva'
        }
    )
    if created:
        anfitriao.set_password('123456')
        anfitriao.save()
    
    # Hóspede
    hospede, created = User.objects.get_or_create(
        username='hospede',
        defaults={
            'email': 'hospede@example.com',
            'first_name': 'Maria',
            'last_name': 'Santos'
        }
    )
    if created:
        hospede.set_password('123456')
        hospede.save()
    
    print(f"   - Usuários criados: {User.objects.count()}")
    
    # Criar imóvel
    print("2. Criando imóvel...")
    
    imovel, created = Imovel.objects.get_or_create(
        tipo='apartamento',
        cidade='São Paulo',
        bairro='Centro',
        rua='Rua das Flores',
        numero='123',
        defaults={
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
            'wifi': True,
            'max_hospedes': 4,
            'camas': 2,
            'tipo_cama': 'Casal',
            'politica_cancelamento': 'moderada',
            'checkin_hora': '14:00',
            'checkout_hora': '11:00',
            'anfitriao': anfitriao,
            'anfitriao_nome': f"{anfitriao.first_name} {anfitriao.last_name}",
            'anfitriao_superhost': True,
            'tempo_anuncio_meses': 6
        }
    )
    
    print(f"   - Imóveis criados: {Imovel.objects.count()}")
    
    # Criar reserva passada (concluída) - usando datas futuras para contornar validação
    print("3. Criando reserva concluída...")
    
    data_checkin_passada = date.today() + timedelta(days=1)
    data_checkout_passada = data_checkin_passada + timedelta(days=3)
    numero_noites = 3
    
    preco_por_noite = imovel.preco_aluguel
    preco_base = preco_por_noite * numero_noites
    taxa_servico = preco_base * Decimal('0.10')
    taxa_limpeza = Decimal('50.00')
    desconto = Decimal('0.00')
    preco_total = preco_base + taxa_servico + taxa_limpeza - desconto
    
    reserva_concluida, created = Reserva.objects.get_or_create(
        imovel=imovel,
        hospede=hospede,
        data_checkin=data_checkin_passada,
        data_checkout=data_checkout_passada,
        defaults={
            'numero_hospedes': 2,
            'preco_total': preco_total,
            'preco_por_noite': preco_por_noite,
            'numero_noites': numero_noites,
            'taxa_limpeza': taxa_limpeza,
            'taxa_servico': taxa_servico,
            'desconto': desconto,
            'status': 'concluida',
            'observacoes': 'Reserva de exemplo concluída'
        }
    )
    
    # Criar reserva futura (pendente)
    print("4. Criando reserva futura...")
    
    data_checkin_futura = date.today() + timedelta(days=20)
    data_checkout_futura = data_checkin_futura + timedelta(days=2)
    numero_noites_futura = 2
    
    preco_base_futura = preco_por_noite * numero_noites_futura
    taxa_servico_futura = preco_base_futura * Decimal('0.10')
    taxa_limpeza_futura = Decimal('50.00')
    desconto_futura = Decimal('0.00')
    preco_total_futura = preco_base_futura + taxa_servico_futura + taxa_limpeza_futura - desconto_futura
    
    reserva_futura, created = Reserva.objects.get_or_create(
        imovel=imovel,
        hospede=hospede,
        data_checkin=data_checkin_futura,
        data_checkout=data_checkout_futura,
        defaults={
            'numero_hospedes': 2,
            'preco_total': preco_total_futura,
            'preco_por_noite': preco_por_noite,
            'numero_noites': numero_noites_futura,
            'taxa_limpeza': taxa_limpeza_futura,
            'taxa_servico': taxa_servico_futura,
            'desconto': desconto_futura,
            'status': 'pendente',
            'observacoes': 'Reserva futura de exemplo'
        }
    )
    
    print(f"   - Reservas criadas: {Reserva.objects.count()}")
    
    # Criar avaliação
    print("5. Criando avaliação...")
    
    avaliacao, created = Avaliacao.objects.get_or_create(
        reserva=reserva_concluida,
        defaults={
            'nota': 5,
            'comentario': 'Excelente estadia! Apartamento muito confortável.',
            'limpeza': 5,
            'comunicacao': 5,
            'localizacao': 4,
            'valor': 5
        }
    )
    
    # Atualizar nota média do imóvel
    if created:
        imovel.nota_media = Decimal('5.00')
        imovel.total_avaliacoes = 1
        imovel.save()
    
    print(f"   - Avaliações criadas: {Avaliacao.objects.count()}")
    
    print("\nDados de exemplo criados com sucesso!")
    print(f"Resumo:")
    print(f"   - Usuarios: {User.objects.count()}")
    print(f"   - Imoveis: {Imovel.objects.count()}")
    print(f"   - Reservas: {Reserva.objects.count()}")
    print(f"   - Avaliacoes: {Avaliacao.objects.count()}")
    
    print(f"\nCredenciais de teste:")
    print(f"   - Anfitriao: anfitriao / 123456")
    print(f"   - Hospede: hospede / 123456")
    
    print(f"\nURLs para testar:")
    print(f"   - Admin: http://127.0.0.1:8000/admin/")
    print(f"   - API Imoveis: http://127.0.0.1:8000/api/imoveis/")
    print(f"   - API Reservas: http://127.0.0.1:8000/api/reservas/")

if __name__ == '__main__':
    main()
