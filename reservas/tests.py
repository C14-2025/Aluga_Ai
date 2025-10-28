from django.test import TestCase
from django.contrib.auth.models import User
from propriedades.models import Propriedade
from .models import Reserva
from django.urls import reverse


class ReservaFlowTests(TestCase):
	def setUp(self):
		self.owner = User.objects.create_user(username="owner", password="pass")
		self.guest = User.objects.create_user(username="guest", password="pass")
		self.guest2 = User.objects.create_user(username="guest2", password="pass")
		self.prop = Propriedade.objects.create(owner=self.owner, titulo="Casa A", preco_por_noite="120.00")

	def test_owner_cannot_reserve_own_property(self):
		self.client.login(username="owner", password="pass")
		url = reverse("reservas:nova", args=[self.prop.pk])
		resp = self.client.post(url, {"inicio": "2025-11-01", "fim": "2025-11-05"}, follow=True)
		self.assertFalse(Reserva.objects.filter(propriedade=self.prop).exists())

	def test_guest_cannot_reserve_inactive_property(self):
		# make prop inactive
		self.prop.ativo = False
		self.prop.save()
		self.client.login(username="guest2", password="pass")
		url = reverse("reservas:nova", args=[self.prop.pk])
		resp = self.client.post(url, {"inicio": "2025-12-01", "fim": "2025-12-05"}, follow=True)
		self.assertFalse(Reserva.objects.filter(propriedade=self.prop).exists())

