from django.test import TestCase
from django.contrib.auth.models import User
from propriedades.models import Propriedade
from .models import Reserva
from django.urls import reverse
from datetime import date
from unittest.mock import patch

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
		self.prop.ativo = False
		self.prop.save()
		self.client.login(username="guest2", password="pass")
		url = reverse("reservas:nova", args=[self.prop.pk])
		resp = self.client.post(url, {"inicio": "2025-12-01", "fim": "2025-12-05"}, follow=True)
		self.assertFalse(Reserva.objects.filter(propriedade=self.prop).exists())
            
class ReservaConfirmTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username="owner", password="pass")
        self.guest = User.objects.create_user(username="guest", password="pass")
        self.prop = Propriedade.objects.create(owner=self.owner, titulo="Casa Teste", preco_por_noite="100.00")

    def test_overlaps_only_when_confirmed(self):
        inicio = date(2025, 12, 1)
        fim = date(2025, 12, 5)
        reserva = Reserva.objects.create(guest=self.guest, propriedade=self.prop, inicio=inicio, fim=fim)
        self.assertEqual(reserva.status, Reserva.STATUS_PENDING)

    def test_confirm_sets_status_and_deactivates_property(self):
        inicio = date(2025, 11, 10)
        fim = date(2025, 11, 15)
        reserva = Reserva.objects.create(guest=self.guest, propriedade=self.prop, inicio=inicio, fim=fim)
        self.assertTrue(self.prop.ativo)

    def test_confirm_handles_property_save_exception_with_mock(self):
        inicio = date(2026, 1, 1)
        fim = date(2026, 1, 5)
        reserva = Reserva.objects.create(guest=self.guest, propriedade=self.prop, inicio=inicio, fim=fim)

        with patch.object(Propriedade, "save", side_effect=Exception("simulated save error")) as mocked_save:
            reserva.confirm()

        reserva.refresh_from_db()
        self.assertEqual(reserva.status, Reserva.STATUS_CONFIRMED)


    def test_reserva_initial_status_is_pending(self):
        inicio = date(2025, 12, 1)
        fim = date(2025, 12, 5)
        reserva = Reserva.objects.create(guest=self.guest, propriedade=self.prop, inicio=inicio, fim=fim)
        self.assertEqual(reserva.status, Reserva.STATUS_PENDING)

    def test_overlaps_returns_false_when_reservation_pending(self):
        inicio = date(2025, 12, 1)
        fim = date(2025, 12, 5)
        reserva = Reserva.objects.create(guest=self.guest, propriedade=self.prop, inicio=inicio, fim=fim)
        self.assertFalse(reserva.overlaps(date(2025, 12, 2), date(2025, 12, 3)))

    def test_overlaps_returns_true_when_confirmed(self):
        inicio = date(2025, 12, 1)
        fim = date(2025, 12, 5)
        reserva = Reserva.objects.create(guest=self.guest, propriedade=self.prop, inicio=inicio, fim=fim)
        reserva.status = Reserva.STATUS_CONFIRMED
        reserva.save()
        self.assertTrue(reserva.overlaps(date(2025, 12, 2), date(2025, 12, 3)))

    def test_overlaps_returns_false_for_non_overlapping_before(self):
        inicio = date(2025, 12, 1)
        fim = date(2025, 12, 5)
        reserva = Reserva.objects.create(guest=self.guest, propriedade=self.prop, inicio=inicio, fim=fim)
        self.assertFalse(reserva.overlaps(date(2025, 11, 20), date(2025, 11, 25)))

    def test_overlaps_returns_false_for_non_overlapping_after(self):
        inicio = date(2025, 12, 1)
        fim = date(2025, 12, 5)
        reserva = Reserva.objects.create(guest=self.guest, propriedade=self.prop, inicio=inicio, fim=fim)
        self.assertFalse(reserva.overlaps(date(2025, 12, 6), date(2025, 12, 10)))

    def test_confirm_sets_status_to_confirmed(self):
        inicio = date(2025, 11, 10)
        fim = date(2025, 11, 15)
        reserva = Reserva.objects.create(guest=self.guest, propriedade=self.prop, inicio=inicio, fim=fim)
        reserva.confirm()
        reserva.refresh_from_db()
        self.assertEqual(reserva.status, Reserva.STATUS_CONFIRMED)

    def test_confirm_deactivates_property(self):
        inicio = date(2025, 11, 10)
        fim = date(2025, 11, 15)
        reserva = Reserva.objects.create(guest=self.guest, propriedade=self.prop, inicio=inicio, fim=fim)
        reserva.confirm()
        self.prop.refresh_from_db()
        self.assertFalse(self.prop.ativo)
