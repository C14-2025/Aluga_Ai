from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from datetime import date, timedelta
from decimal import Decimal
from .models import Imovel, Reserva, Avaliacao

class ImovelModelTest(TestCase):
    """Testes para o modelo Imovel"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.imovel = Imovel.objects.create(
            tipo='apartamento',
            cidade='São Paulo',
            bairro='Centro',
            rua='Rua das Flores',
            numero='123',
            cep='01234-567',
            quartos=2,
            banheiros=1,
            area_m2=60,
            preco_aluguel=Decimal('1500.00'),
            descricao='Apartamento aconchegante',
            max_hospedes=4,
            camas=2,
            tipo_cama='Casal',
            anfitriao=self.user,
            anfitriao_nome='João Silva',
            ano_construcao=2020
        )
    
    def test_imovel_creation(self):
        """Testar criação de imóvel"""
        self.assertEqual(self.imovel.tipo, 'apartamento')
        self.assertEqual(self.imovel.cidade, 'São Paulo')
        self.assertEqual(self.imovel.anfitriao, self.user)
    
    def test_endereco_completo(self):
        """Testar propriedade endereco_completo"""
        expected = "Rua das Flores, 123 - Centro, São Paulo"
        self.assertEqual(self.imovel.endereco_completo, expected)
    
    def test_preco_total_mensal(self):
        """Testar cálculo do preço total mensal"""
        self.imovel.condominio = Decimal('200.00')
        self.imovel.iptu = Decimal('100.00')
        self.imovel.save()
        
        expected = Decimal('1800.00')  # 1500 + 200 + 100
        self.assertEqual(self.imovel.preco_total_mensal, expected)

class ReservaModelTest(TestCase):
    """Testes para o modelo Reserva"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.imovel = Imovel.objects.create(
            tipo='apartamento',
            cidade='São Paulo',
            bairro='Centro',
            rua='Rua das Flores',
            numero='123',
            cep='01234-567',
            quartos=2,
            banheiros=1,
            area_m2=60,
            preco_aluguel=Decimal('1500.00'),
            descricao='Apartamento aconchegante',
            max_hospedes=4,
            camas=2,
            tipo_cama='Casal',
            anfitriao=self.user,
            anfitriao_nome='João Silva',
            ano_construcao=2020
        )
        
        self.reserva = Reserva.objects.create(
            imovel=self.imovel,
            hospede=self.user,
            data_checkin=date.today() + timedelta(days=7),
            data_checkout=date.today() + timedelta(days=10),
            numero_hospedes=2,
            preco_total=Decimal('4500.00'),
            preco_por_noite=Decimal('1500.00'),
            numero_noites=3
        )
    
    def test_reserva_creation(self):
        """Testar criação de reserva"""
        self.assertEqual(self.reserva.imovel, self.imovel)
        self.assertEqual(self.reserva.hospede, self.user)
        self.assertEqual(self.reserva.status, 'pendente')
    
    def test_pode_cancelar(self):
        """Testar propriedade pode_cancelar"""
        # Reserva futura pode ser cancelada
        self.assertTrue(self.reserva.pode_cancelar)
        
        # Reserva no passado não pode ser cancelada
        self.reserva.data_checkin = date.today() - timedelta(days=1)
        self.reserva.save()
        self.assertFalse(self.reserva.pode_cancelar)
    
    def test_esta_ativa(self):
        """Testar propriedade esta_ativa"""
        # Reserva confirmada no período atual
        self.reserva.status = 'confirmada'
        self.reserva.data_checkin = date.today()
        self.reserva.data_checkout = date.today() + timedelta(days=1)
        self.reserva.save()
        self.assertTrue(self.reserva.esta_ativa)

class ReservaAPITest(APITestCase):
    """Testes para a API de reservas"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.anfitriao = User.objects.create_user(
            username='anfitriao',
            email='anfitriao@example.com',
            password='testpass123'
        )
        
        self.imovel = Imovel.objects.create(
            tipo='apartamento',
            cidade='São Paulo',
            bairro='Centro',
            rua='Rua das Flores',
            numero='123',
            cep='01234-567',
            quartos=2,
            banheiros=1,
            area_m2=60,
            preco_aluguel=Decimal('1500.00'),
            descricao='Apartamento aconchegante',
            max_hospedes=4,
            camas=2,
            tipo_cama='Casal',
            anfitriao=self.anfitriao,
            anfitriao_nome='João Silva',
            ano_construcao=2020
        )
    
    def test_listar_imoveis(self):
        """Testar listagem de imóveis"""
        url = reverse('imovel-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_criar_reserva_autenticado(self):
        """Testar criação de reserva com usuário autenticado"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('reserva-list')
        data = {
            'imovel': self.imovel.id,
            'data_checkin': (date.today() + timedelta(days=7)).isoformat(),
            'data_checkout': (date.today() + timedelta(days=10)).isoformat(),
            'numero_hospedes': 2,
            'observacoes': 'Reserva de teste'
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Reserva.objects.count(), 1)
    
    def test_criar_reserva_nao_autenticado(self):
        """Testar criação de reserva sem autenticação"""
        url = reverse('reserva-list')
        data = {
            'imovel': self.imovel.id,
            'data_checkin': (date.today() + timedelta(days=7)).isoformat(),
            'data_checkout': (date.today() + timedelta(days=10)).isoformat(),
            'numero_hospedes': 2
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_verificar_disponibilidade(self):
        """Testar verificação de disponibilidade"""
        url = reverse('imovel-disponibilidade', kwargs={'pk': self.imovel.id})
        params = {
            'checkin': (date.today() + timedelta(days=7)).isoformat(),
            'checkout': (date.today() + timedelta(days=10)).isoformat()
        }
        
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['disponivel'])
    
    def test_filtrar_imoveis_por_cidade(self):
        """Testar filtro de imóveis por cidade"""
        url = reverse('imovel-list')
        response = self.client.get(url, {'cidade': 'São Paulo'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_filtrar_imoveis_por_preco(self):
        """Testar filtro de imóveis por faixa de preço"""
        url = reverse('imovel-list')
        response = self.client.get(url, {'preco_min': '1000', 'preco_max': '2000'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
    
    def test_confirmar_reserva_anfitriao(self):
        """Testar confirmação de reserva pelo anfitrião"""
        # Criar reserva
        reserva = Reserva.objects.create(
            imovel=self.imovel,
            hospede=self.user,
            data_checkin=date.today() + timedelta(days=7),
            data_checkout=date.today() + timedelta(days=10),
            numero_hospedes=2,
            preco_total=Decimal('4500.00'),
            preco_por_noite=Decimal('1500.00'),
            numero_noites=3
        )
        
        # Anfitrião confirma reserva
        self.client.force_authenticate(user=self.anfitriao)
        url = reverse('reserva-confirmar', kwargs={'pk': reserva.id})
        response = self.client.post(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, 'confirmada')
    
    def test_cancelar_reserva(self):
        """Testar cancelamento de reserva"""
        # Criar reserva
        reserva = Reserva.objects.create(
            imovel=self.imovel,
            hospede=self.user,
            data_checkin=date.today() + timedelta(days=7),
            data_checkout=date.today() + timedelta(days=10),
            numero_hospedes=2,
            preco_total=Decimal('4500.00'),
            preco_por_noite=Decimal('1500.00'),
            numero_noites=3
        )
        
        # Hóspede cancela reserva
        self.client.force_authenticate(user=self.user)
        url = reverse('reserva-cancelar', kwargs={'pk': reserva.id})
        data = {'motivo': 'Mudança de planos'}
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, 'cancelada')
        self.assertEqual(reserva.motivo_cancelamento, 'Mudança de planos')

class AvaliacaoAPITest(APITestCase):
    """Testes para a API de avaliações"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.anfitriao = User.objects.create_user(
            username='anfitriao',
            email='anfitriao@example.com',
            password='testpass123'
        )
        
        self.imovel = Imovel.objects.create(
            tipo='apartamento',
            cidade='São Paulo',
            bairro='Centro',
            rua='Rua das Flores',
            numero='123',
            cep='01234-567',
            quartos=2,
            banheiros=1,
            area_m2=60,
            preco_aluguel=Decimal('1500.00'),
            descricao='Apartamento aconchegante',
            max_hospedes=4,
            camas=2,
            tipo_cama='Casal',
            anfitriao=self.anfitriao,
            anfitriao_nome='João Silva',
            ano_construcao=2020
        )
        
        self.reserva = Reserva.objects.create(
            imovel=self.imovel,
            hospede=self.user,
            data_checkin=date.today() - timedelta(days=10),
            data_checkout=date.today() - timedelta(days=7),
            numero_hospedes=2,
            preco_total=Decimal('4500.00'),
            preco_por_noite=Decimal('1500.00'),
            numero_noites=3,
            status='concluida'
        )
    
    def test_criar_avaliacao(self):
        """Testar criação de avaliação"""
        self.client.force_authenticate(user=self.user)
        
        url = reverse('avaliacao-list')
        data = {
            'reserva': self.reserva.id,
            'nota': 5,
            'comentario': 'Excelente estadia!',
            'limpeza': 5,
            'comunicacao': 5,
            'localizacao': 4,
            'valor': 5
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Avaliacao.objects.count(), 1)
        
        # Verificar se a nota média do imóvel foi atualizada
        self.imovel.refresh_from_db()
        self.assertEqual(self.imovel.nota_media, Decimal('5.00'))
        self.assertEqual(self.imovel.total_avaliacoes, 1)
    
    def test_avaliacao_reserva_nao_concluida(self):
        """Testar avaliação de reserva não concluída"""
        self.reserva.status = 'confirmada'
        self.reserva.save()
        
        self.client.force_authenticate(user=self.user)
        
        url = reverse('avaliacao-list')
        data = {
            'reserva': self.reserva.id,
            'nota': 5,
            'comentario': 'Excelente estadia!',
            'limpeza': 5,
            'comunicacao': 5,
            'localizacao': 4,
            'valor': 5
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_avaliacao_duplicada(self):
        """Testar avaliação duplicada"""
        # Criar primeira avaliação
        Avaliacao.objects.create(
            reserva=self.reserva,
            nota=5,
            comentario='Excelente!',
            limpeza=5,
            comunicacao=5,
            localizacao=5,
            valor=5
        )
        
        self.client.force_authenticate(user=self.user)
        
        url = reverse('avaliacao-list')
        data = {
            'reserva': self.reserva.id,
            'nota': 4,
            'comentario': 'Boa estadia!',
            'limpeza': 4,
            'comunicacao': 4,
            'localizacao': 4,
            'valor': 4
        }
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)