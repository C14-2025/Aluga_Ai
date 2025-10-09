from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid

class Imovel(models.Model):
    """Modelo para representar um imóvel disponível para aluguel"""
    
    TIPO_CHOICES = [
        ('apartamento', 'Apartamento'),
        ('casa', 'Casa'),
        ('studio', 'Studio'),
        ('loft', 'Loft'),
    ]
    
    STATUS_CHOICES = [
        ('ativo', 'Ativo'),
        ('inativo', 'Inativo'),
        ('manutencao', 'Em Manutenção'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES)
    
    # Endereço
    cidade = models.CharField(max_length=100)
    bairro = models.CharField(max_length=100)
    rua = models.CharField(max_length=200)
    numero = models.CharField(max_length=20)
    cep = models.CharField(max_length=10)
    complemento = models.CharField(max_length=100, blank=True, null=True)
    latitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=10, decimal_places=6, null=True, blank=True)
    
    # Características do imóvel
    quartos = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    banheiros = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    vagas_garagem = models.PositiveIntegerField(default=0)
    area_m2 = models.PositiveIntegerField()
    andar = models.IntegerField(default=0)
    ano_construcao = models.PositiveIntegerField()
    
    # Preços e custos
    preco_aluguel = models.DecimalField(max_digits=10, decimal_places=2)
    condominio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iptu = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Detalhes
    descricao = models.TextField()
    comodidades = models.JSONField(default=list)  # Lista de comodidades
    regras_casa = models.JSONField(default=list)  # Lista de regras
    tags = models.JSONField(default=list)  # Tags do imóvel
    
    # Status e disponibilidade
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ativo')
    mobiliado = models.BooleanField(default=False)
    aceita_pets = models.BooleanField(default=False)
    wifi = models.BooleanField(default=True)
    
    # Capacidade
    max_hospedes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    camas = models.PositiveIntegerField()
    tipo_cama = models.CharField(max_length=50)
    
    # Políticas
    politica_cancelamento = models.CharField(max_length=50, default='moderada')
    checkin_hora = models.TimeField(default='14:00')
    checkout_hora = models.TimeField(default='11:00')
    
    # Avaliações
    nota_media = models.DecimalField(max_digits=3, decimal_places=2, default=0.00, 
                                   validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])
    total_avaliacoes = models.PositiveIntegerField(default=0)
    
    # Anfitrião
    anfitriao = models.ForeignKey(User, on_delete=models.CASCADE, related_name='imoveis')
    anfitriao_nome = models.CharField(max_length=100)
    anfitriao_superhost = models.BooleanField(default=False)
    
    # Metadados
    tempo_anuncio_meses = models.PositiveIntegerField(default=0)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Imóvel'
        verbose_name_plural = 'Imóveis'
    
    def __str__(self):
        return f"{self.tipo.title()} em {self.cidade} - {self.bairro}"
    
    @property
    def endereco_completo(self):
        return f"{self.rua}, {self.numero} - {self.bairro}, {self.cidade}"
    
    @property
    def preco_total_mensal(self):
        return self.preco_aluguel + self.condominio + self.iptu

class Reserva(models.Model):
    """Modelo para representar uma reserva de imóvel"""
    
    STATUS_CHOICES = [
        ('pendente', 'Pendente'),
        ('confirmada', 'Confirmada'),
        ('cancelada', 'Cancelada'),
        ('concluida', 'Concluída'),
        ('rejeitada', 'Rejeitada'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    imovel = models.ForeignKey(Imovel, on_delete=models.CASCADE, related_name='reservas')
    hospede = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reservas')
    
    # Datas da reserva
    data_checkin = models.DateField()
    data_checkout = models.DateField()
    numero_hospedes = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    
    # Status e valores
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pendente')
    preco_total = models.DecimalField(max_digits=10, decimal_places=2)
    preco_por_noite = models.DecimalField(max_digits=10, decimal_places=2)
    numero_noites = models.PositiveIntegerField()
    
    # Taxas e descontos
    taxa_limpeza = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    taxa_servico = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    desconto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    # Observações
    observacoes = models.TextField(blank=True, null=True)
    motivo_cancelamento = models.TextField(blank=True, null=True)
    
    # Metadados
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    confirmado_em = models.DateTimeField(null=True, blank=True)
    cancelado_em = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-criado_em']
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'
        # Evitar reservas duplicadas para o mesmo período
        unique_together = ['imovel', 'data_checkin', 'data_checkout']
    
    def __str__(self):
        return f"Reserva {self.id} - {self.imovel} ({self.data_checkin} a {self.data_checkout})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        from datetime import date
        
        # Validar datas
        if self.data_checkin and self.data_checkout:
            if self.data_checkin < date.today():
                raise ValidationError("Data de check-in não pode ser no passado")
            if self.data_checkout <= self.data_checkin:
                raise ValidationError("Data de checkout deve ser posterior ao check-in")
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    @property
    def pode_cancelar(self):
        """Verifica se a reserva pode ser cancelada"""
        from datetime import date, timedelta
        return (self.status in ['pendente', 'confirmada'] and 
                self.data_checkin > date.today() + timedelta(days=1))
    
    @property
    def esta_ativa(self):
        """Verifica se a reserva está ativa"""
        from datetime import date
        return (self.status == 'confirmada' and 
                self.data_checkin <= date.today() <= self.data_checkout)

class Avaliacao(models.Model):
    """Modelo para avaliações de imóveis"""
    
    reserva = models.OneToOneField(Reserva, on_delete=models.CASCADE, related_name='avaliacao')
    nota = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comentario = models.TextField(blank=True, null=True)
    limpeza = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comunicacao = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    localizacao = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    valor = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    
    criado_em = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Avaliação'
        verbose_name_plural = 'Avaliações'
    
    def __str__(self):
        return f"Avaliação {self.nota}/5 - {self.reserva.imovel}"
