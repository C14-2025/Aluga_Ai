import pytest
from types import SimpleNamespace
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.db import IntegrityError

@pytest.mark.django_db
def test_register_view_mock_success(monkeypatch):
    """
    Mocka User.objects.create_user para não tocar o DB.
    A view deve retornar 201 e incluir o username no body.
    """
    def fake_create_user(username, email='', password=None, **extra):
        return SimpleNamespace(username=username, email=email)

    monkeypatch.setattr('usuarios.serializers.User.objects.create_user', fake_create_user)

    client = APIClient()
    url = reverse('register')
    payload = {'username': 'mockuser', 'password': 'senha123', 'email': 'm@ex.com'}
    resp = client.post(url, payload, format='json')

    assert resp.status_code == status.HTTP_201_CREATED
    assert resp.data['username'] == 'mockuser'

@pytest.mark.django_db
def test_register_serializer_create_mock(monkeypatch):
    """
    Testa diretamente o RegisterSerializer.create sem usar view.
    """
    from usuarios.serializers import RegisterSerializer

    def fake_create_user(username, email='', password=None, **extra):
        return SimpleNamespace(username=username, email=email)

    monkeypatch.setattr('usuarios.serializers.User.objects.create_user', fake_create_user)

    data = {'username': 'suser', 'password': '12345', 'email': 's@e.com'}
    serializer = RegisterSerializer(data=data)
    assert serializer.is_valid(raise_exception=True)
    user = serializer.save()  
    assert user.username == 'suser'
    assert user.email == 's@e.com'
