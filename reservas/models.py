from django.contrib.auth.models import User
from django.db import models
from propriedades.models import Propriedade

class Reserva(models.Model):
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservas_feitas")
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name="reservas")
    inicio = models.DateField()
    fim = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    confirmada = models.BooleanField(default=False)

    def __str__(self):
        return f"Reserva {self.id} - {self.guest} -> {self.propriedade}"
