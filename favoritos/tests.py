import json
from unittest.mock import patch
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from propriedades.models import Propriedade
from favoritos.models import Favorito


class FavoritosViewTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        # Usuário que vai realizar os testes
        cls.user = User.objects.create_user(
            username="john",
            password="123456"
        )

        # Dono da propriedade (campo obrigatório no modelo Propriedade)
        cls.owner = User.objects.create_user(
            username="owneruser",
            password="123456"
        )

        # Criar propriedade ativa
        cls.prop = Propriedade.objects.create(
            titulo="Casa Teste",
            preco_por_noite=150.0,
            ativo=True,
            owner=cls.owner  # campo obrigatório
        )

        cls.add_url = reverse("favoritos:add", args=[cls.prop.id])
        cls.remove_url = reverse("favoritos:remove", args=[cls.prop.id])
        cls.list_url = reverse("favoritos:list")

    # ----------------------------------------------------------------------
    # ADD FAVORITO
    # ----------------------------------------------------------------------

    @patch("favoritos.views.compute_personal_recommendations_for_user")
    def test_add_favorito_success(self, mock_recs):

        mock_recs.return_value = {
            "results": [{"id": 1, "score": 0.9}],
            "avg_price": 250
        }

        client = Client()
        client.login(username="john", password="123456")

        response = client.post(self.add_url)
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertTrue(data["favorited"])
        self.assertTrue(data["created"])
        self.assertEqual(len(data["recommendations"]), 1)

        # Favorito é realmente criado
        self.assertEqual(Favorito.objects.count(), 1)

    @patch("favoritos.views.compute_personal_recommendations_for_user")
    def test_add_favorito_duplicate(self, mock_recs):

        mock_recs.return_value = {"results": [], "avg_price": None}

        # criar antes
        Favorito.objects.create(user=self.user, propriedade=self.prop)

        client = Client()
        client.login(username="john", password="123456")

        response = client.post(self.add_url)
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(data["created"])  # já existia
        self.assertEqual(Favorito.objects.count(), 1)

    # ----------------------------------------------------------------------
    # REMOVE FAVORITO
    # ----------------------------------------------------------------------

    @patch("favoritos.views.compute_personal_recommendations_for_user")
    def test_remove_favorito_success(self, mock_recs):

        mock_recs.return_value = {"results": [], "avg_price": None}

        Favorito.objects.create(user=self.user, propriedade=self.prop)

        client = Client()
        client.login(username="john", password="123456")

        response = client.post(self.remove_url)
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertFalse(data["favorited"])
        self.assertEqual(Favorito.objects.count(), 0)

    # ----------------------------------------------------------------------
    # LIST FAVORITOS
    # ----------------------------------------------------------------------

    def test_list_favoritos(self):

        # Criar mais uma propriedade válida
        prop2 = Propriedade.objects.create(
            titulo="Casa 2",
            preco_por_noite=300.0,
            ativo=True,
            owner=self.owner
        )

        # Criar favoritos
        Favorito.objects.create(user=self.user, propriedade=self.prop)
        Favorito.objects.create(user=self.user, propriedade=prop2)

        client = Client()
        client.login(username="john", password="123456")

        response = client.get(self.list_url)
        data = json.loads(response.content)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(data["results"]), 2)

        first = data["results"][0]
        self.assertIn("id", first)
        self.assertIn("titulo", first)
        self.assertIn("preco_por_noite", first)

    # ----------------------------------------------------------------------
    # TESTES DE AUTENTICAÇÃO
    # ----------------------------------------------------------------------

    def test_add_requires_login(self):
        client = Client()
        response = client.post(self.add_url)
        self.assertEqual(response.status_code, 302)  # redirect login

    def test_remove_requires_login(self):
        client = Client()
        response = client.post(self.remove_url)
        self.assertEqual(response.status_code, 302)

    def test_list_requires_login(self):
        client = Client()
        response = client.get(self.list_url)
        self.assertEqual(response.status_code, 302)