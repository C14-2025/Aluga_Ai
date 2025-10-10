from django.contrib import admin
from .models import Propriedade, PropriedadeImagem

class ImagemInline(admin.TabularInline):
    model = PropriedadeImagem
    extra = 1

@admin.register(Propriedade)
class PropriedadeAdmin(admin.ModelAdmin):
    inlines = [ImagemInline]
    list_display = ("titulo", "owner", "preco_por_noite", "ativo")
