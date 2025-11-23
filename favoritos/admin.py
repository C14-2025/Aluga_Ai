from django.contrib import admin
from .models import Favorito, UserRecommendation

@admin.register(Favorito)
class FavoritoAdmin(admin.ModelAdmin):
    list_display = ('user', 'propriedade', 'criado_em')
    search_fields = ('user__username', 'propriedade__titulo')

@admin.register(UserRecommendation)
class UserRecommendationAdmin(admin.ModelAdmin):
    list_display = ('user', 'propriedade', 'score', 'predicted_price', 'generated_at', 'source')
    list_filter = ('source', 'generated_at')
    search_fields = ('user__username', 'propriedade__titulo')
