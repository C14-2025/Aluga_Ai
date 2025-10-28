from django.test import TestCase
from django.contrib.auth.models import User


class UsuariosTests(TestCase):
	def test_user_creation_and_profile(self):
		u = User.objects.create_user(username="jose", password="senha")
		self.assertIsNotNone(u)
		self.assertEqual(u.username, "jose")

