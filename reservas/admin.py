from django.contrib import admin
from .models import Reserva

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ("id", "guest", "propriedade", "inicio", "fim", "status", "criado_em")
