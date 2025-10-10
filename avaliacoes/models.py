from django.contrib.auth.models import User
from django.db import models
from propriedades.models import Propriedade

class Avaliacao(models.Model):
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="avaliacoes_feitas")
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name="avaliacoes")
    nota = models.IntegerField()  # 1-5
    comentario = models.TextField(blank=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Aval {self.nota} por {self.autor}"
