from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import RegisterSerializer, UserListSerializer

class UsuarioTests(APITestCase):
    def test_cadastro_usuario_sucesso(self):
        url = reverse('register')
        data = {'username': 'Alvaro', 'password': 'TestPass123', 'confirm_password': 'TestPass123', 'email': 'Alvarocarel@email.com'}
        response = self.client.post(url, data, format='json')
        print(response.data)  # Adicione esta linha
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'Alvaro')

    def test_cadastro_usuario_existente(self):
        User.objects.create_user(username='Alvaro', password='naao sei', email='Alvarocarel@email.com')
        url = reverse('register')
        data = {'username': 'Alvaro', 'password': 'naao sei', 'email': 'Alvarocarel@email.com'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_usuario(self):
        User.objects.create_user(username='Alvaro', password='naao sei', email='Alvarocarel@email.com')
        url = reverse('token_obtain_pair')
        data = {'username': 'Alvaro', 'password': 'naao sei'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_login_senha_errada(self):
        User.objects.create_user(username='Alvaro', password='naao sei')
        url = reverse('token_obtain_pair')
        data = {'username': 'Alvaro', 'password': 'senha_errada'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn('detail', response.data)

    def test_login_outro_usuario(self):
        User.objects.create_user(username='Maria', password='senhaMaria')
        url = reverse('token_obtain_pair')
        data = {'username': 'Maria', 'password': 'senhaMaria'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)


class UserValidationTestCase(APITestCase):
    """Testes para as novas validações de usuário"""
    
    def test_user_registration_with_confirm_password(self):
        """Teste de registro com confirmação de senha"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='testuser').exists())

    def test_user_registration_invalid_email_format(self):
        """Teste de registro com formato de email inválido"""
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_weak_password(self):
        """Teste de registro com senha fraca"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': '123',
            'confirm_password': '123'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_password_mismatch(self):
        """Teste de registro com senhas diferentes"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'confirm_password': 'DifferentPass123'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_registration_duplicate_email(self):
        """Teste de registro com email duplicado"""
        # Criar usuário inicial
        User.objects.create_user(
            username='existing',
            email='test@example.com',
            password='TestPass123'
        )
        
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        }
        response = self.client.post('/api/register/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserListTestCase(APITestCase):
    """Testes para a listagem de usuários"""
    
    def setUp(self):
        """Configuração inicial para os testes"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        self.token = RefreshToken.for_user(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token.access_token}')

    def test_user_list_authenticated(self):
        """Teste de listagem de usuários autenticado"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Com paginação, os dados ficam em 'results'
        if 'results' in response.data:
            self.assertIn('results', response.data)
        else:
            # Se não há paginação, deve ser uma lista direta
            self.assertIsInstance(response.data, list)

    def test_user_list_unauthenticated(self):
        """Teste de listagem de usuários sem autenticação"""
        self.client.credentials()  # Remove autenticação
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_list_filter_by_username(self):
        """Teste de filtro por username"""
        # Criar outro usuário
        User.objects.create_user(
            username='anotheruser',
            email='another@example.com',
            password='TestPass123'
        )
        
        response = self.client.get('/api/users/?username=test')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar se os dados estão em 'results' (paginação) ou lista direta
        if 'results' in response.data:
            users = response.data['results']
        else:
            users = response.data
            
        # Deve retornar apenas usuários com 'test' no username
        usernames = [user['username'] for user in users]
        self.assertTrue(all('test' in username.lower() for username in usernames))


class SerializerTestCase(TestCase):
    """Testes para os serializers"""
    
    def test_register_serializer_valid_data(self):
        """Teste do serializer com dados válidos"""
        data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_register_serializer_invalid_email_format(self):
        """Teste do serializer com formato de email inválido"""
        data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password': 'TestPass123',
            'confirm_password': 'TestPass123'
        }
        serializer = RegisterSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('email', serializer.errors)

    def test_user_list_serializer_fields(self):
        """Teste dos campos do serializer de listagem"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='TestPass123'
        )
        serializer = UserListSerializer(user)
        expected_fields = {'id', 'username', 'email', 'date_joined', 'is_active'}
        self.assertEqual(set(serializer.data.keys()), expected_fields)
