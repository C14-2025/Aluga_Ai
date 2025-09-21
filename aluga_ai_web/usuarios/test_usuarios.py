from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth.models import User

class UsuarioTests(APITestCase):
    def test_cadastro_usuario_sucesso(self):
        url = reverse('register')
        data = {'username': 'Alvaro', 'password': 'naao sei', 'email': 'Alvarocarel@email.com'}
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
