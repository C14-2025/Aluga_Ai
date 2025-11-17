from django.test import TestCase
from django.contrib.auth.models import User
from .models import Propriedade
from .forms import PropriedadeForm


class PropriedadeModelTests(TestCase):
	def test_create_property_sets_owner_and_defaults(self):
		owner = User.objects.create_user(username="owner", password="pass")
		p = Propriedade.objects.create(owner=owner, titulo="Casa Teste", preco_por_noite="100.00")
		self.assertEqual(p.owner, owner)
		self.assertTrue(p.ativo)
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
