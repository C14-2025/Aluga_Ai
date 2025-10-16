from django.db import models

class Usuario(models.Model):
    """The user."""
    nome = models.CharField(max_length=200)
    senha = models.CharField(max_length=200)
    email = models.EmailField(max_length=200)

    def __str__(self):
        """Return a string representation of the model."""
        return self.text

class Imovel(models.Model):
    """Imovel disponivel."""
    nome = models.CharField(max_length=200)
    descricao = models.TextField()
    endereco = models.CharField(max_length=200)
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        """Return a string representation of the model."""
        return self.text