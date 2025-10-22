from django.db import models
from django.contrib.auth.models import User

class Propriedade(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="propriedades")
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    endereco = models.CharField(max_length=300, blank=True)
    city = models.CharField("Cidade", max_length=100, blank=True)
    state = models.CharField("Estado", max_length=100, blank=True)
    preco_por_noite = models.DecimalField(max_digits=8, decimal_places=2)
    criado_em = models.DateTimeField(auto_now_add=True)
    ativo = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.titulo} - {self.owner.username}"

class PropriedadeImagem(models.Model):
    propriedade = models.ForeignKey(Propriedade, on_delete=models.CASCADE, related_name="imagens")
    imagem = models.ImageField(upload_to="propriedades/")
    legenda = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"Imagem {self.propriedade} ({self.legenda})"
