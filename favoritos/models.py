from django.db import models
from django.contrib.auth.models import User
from propriedades.models import Propriedade


class Favorito(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritos')
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='favoritado_por')
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'propriedade')
        verbose_name = 'Favorito'
        verbose_name_plural = 'Favoritos'

    def __str__(self):
        return f"{self.user.username} -> {self.propriedade.titulo}"


class UserRecommendation(models.Model):
    """Persistência de recomendações personalizadas geradas para um usuário.

    Armazena os top-N resultados com score e preço previsto para reaproveitar em reloads rápidos.
    Recomputação pode ocorrer se registros estiverem antigos (> 6h) ou se favoritos mudarem.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recomendacoes_persistidas')
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name='recomendacoes_para_usuario')
    score = models.FloatField()
    predicted_price = models.DecimalField(max_digits=10, decimal_places=2)
    generated_at = models.DateTimeField(auto_now_add=True)
    source = models.CharField(max_length=30, default='personal')

    class Meta:
        unique_together = ('user', 'propriedade', 'source')
        indexes = [
            models.Index(fields=['user', 'source']),
            models.Index(fields=['generated_at']),
        ]
        verbose_name = 'Recomendação de Usuário'
        verbose_name_plural = 'Recomendações de Usuário'

    def __str__(self):
        return f"Rec {self.user.username} -> {self.propriedade_id} ({self.score})"
