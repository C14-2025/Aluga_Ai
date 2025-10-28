from django.test import TestCase
from django.contrib.auth.models import User
from .models import Propriedade


class PropriedadeModelTests(TestCase):
	def test_create_property_sets_owner_and_defaults(self):
		owner = User.objects.create_user(username="owner", password="pass")
		p = Propriedade.objects.create(owner=owner, titulo="Casa Teste", preco_por_noite="100.00")
		self.assertEqual(p.owner, owner)
		self.assertTrue(p.ativo)
		self.assertEqual(str(p), f"{p.titulo} - {owner.username}")

