from django.test import TestCase
from django.contrib.auth.models import User
from .models import Propriedade
from .forms import PropriedadeForm
from django.urls import reverse


class PropriedadeModelTests(TestCase):
    def test_create_property_sets_owner(self):
        owner = User.objects.create_user(username="owner", password="pass")
        p = Propriedade.objects.create(owner=owner, titulo="Casa Teste", preco_por_noite="100.00")
        self.assertEqual(p.owner, owner)

    def test_create_property_default_ativo_true(self):
        owner = User.objects.create_user(username="owner2", password="pass")
        p = Propriedade.objects.create(owner=owner, titulo="Casa Teste 2", preco_por_noite="200.00")
        self.assertTrue(p.ativo)

    def test_str_representation_includes_title_and_owner(self):
        owner = User.objects.create_user(username="owner3", password="pass")
        p = Propriedade.objects.create(owner=owner, titulo="Casa Teste 3", preco_por_noite="300.00")
        self.assertEqual(str(p), f"{p.titulo} - {owner.username}")

class PropriedadesFormTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u1", password="pass")

    def test_propriedade_form_valid_with_minimal_fields(self):
        """O form deve ser válido quando os campos obrigatórios são fornecidos."""
        data = {
            "titulo": "Apartamento Teste",
            "preco_por_noite": "150.00",
        }
        form = PropriedadeForm(data=data)
        self.assertTrue(form.is_valid())

    def test_propriedade_form_invalid_without_preco_por_noite(self):
        """O form deve ser inválido se o preço por noite não for fornecido."""
        data = {"titulo": "Sem Preço"}
        form = PropriedadeForm(data=data)
        self.assertFalse(form.is_valid())

    # View/template tests
    def test_lista_propriedades_renders_lista_template(self):
        resp = self.client.get(reverse("propriedades:lista"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "propriedades/lista.html")

    def test_detalhe_propriedade_renders_detalhe_template(self):
        owner = User.objects.create_user(username="detuser", password="pass")
        p = Propriedade.objects.create(owner=owner, titulo="Casa Detalhe", preco_por_noite="50.00")
        resp = self.client.get(reverse("propriedades:detalhe", args=[p.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "propriedades/detalhe.html")

    def test_criar_propriedade_get_renders_criar_template(self):
        self.client.login(username=self.user.username, password="pass")
        resp = self.client.get(reverse("propriedades:nova"))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "propriedades/criar.html")

    def test_excluir_propriedade_get_renders_confirm_delete_template(self):
        owner = User.objects.create_user(username="owner_del", password="pass")
        p = Propriedade.objects.create(owner=owner, titulo="Para Excluir", preco_por_noite="60.00")
        self.client.login(username=owner.username, password="pass")
        resp = self.client.get(reverse("propriedades:excluir", args=[p.pk]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, "propriedades/confirm_delete.html")
