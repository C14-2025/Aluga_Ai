from django.db import models
from django.contrib.auth.models import User
from propriedades.models import Propriedade

class Reserva(models.Model):
    STATUS_CHOICES = [
        ("CONFIRMADA", "Confirmada"),
        ("CANCELADA", "Cancelada"),
    ]
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservas_feitas")
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name="reservas")
    inicio = models.DateField()
    fim = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="CONFIRMADA")  # fluxo imediato

    def __str__(self):
        return f"Reserva {self.pk} - {self.guest} -> {self.propriedade}"
