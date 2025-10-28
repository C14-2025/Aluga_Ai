from django.db import models
from django.contrib.auth.models import User
from propriedades.models import Propriedade

class Reserva(models.Model):
    STATUS_PENDING = "PENDING"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_CANCELLED = "CANCELLED"

    STATUS_CHOICES = [
        (STATUS_PENDING, "Pendente"),
        (STATUS_CONFIRMED, "Confirmada"),
        (STATUS_CANCELLED, "Cancelada"),
    ]

    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reservas_feitas")
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name="reservas")
    inicio = models.DateField()
    fim = models.DateField()
    criado_em = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)

    def __str__(self):
        return f"Reserva {self.pk} - {self.guest} -> {self.propriedade} [{self.status}]"

    def overlaps(self, inicio, fim):
        """Retorna True se as datas dadas sobrepõem esta reserva (considerando apenas CONFIRMED)."""
        if self.status != self.STATUS_CONFIRMED:
            return False
        return not (self.fim < inicio or self.inicio > fim)

    def confirm(self):
        self.status = self.STATUS_CONFIRMED
        self.save()
        try:
            prop = self.propriedade
            prop.ativo = False
            prop.save()
        except Exception:
            pass

    def cancel(self):
        self.status = self.STATUS_CANCELLED
        self.save()
        try:
            prop = self.propriedade
            # ao cancelar, reativar a propriedade
            prop.ativo = True
            prop.save()
        except Exception:
            pass
