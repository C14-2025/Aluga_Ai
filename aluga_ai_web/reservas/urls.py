from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Configurar router para ViewSets
router = DefaultRouter()
router.register(r'imoveis', views.ImovelViewSet, basename='imovel')
router.register(r'reservas', views.ReservaViewSet, basename='reserva')
router.register(r'avaliacoes', views.AvaliacaoViewSet, basename='avaliacao')

urlpatterns = [
    # Incluir rotas do router
    path('', include(router.urls)),
    
    # Rotas adicionais específicas
    path('imoveis/<uuid:pk>/disponibilidade/', 
         views.ImovelViewSet.as_view({'get': 'disponibilidade'}), 
         name='imovel-disponibilidade'),
    path('imoveis/<uuid:pk>/avaliacoes/', 
         views.ImovelViewSet.as_view({'get': 'avaliacoes'}), 
         name='imovel-avaliacoes'),
    path('reservas/<uuid:pk>/confirmar/', 
         views.ReservaViewSet.as_view({'post': 'confirmar'}), 
         name='reserva-confirmar'),
    path('reservas/<uuid:pk>/cancelar/', 
         views.ReservaViewSet.as_view({'post': 'cancelar'}), 
         name='reserva-cancelar'),
    path('reservas/<uuid:pk>/concluir/', 
         views.ReservaViewSet.as_view({'post': 'concluir'}), 
         name='reserva-concluir'),
    path('reservas/minhas/', 
         views.ReservaViewSet.as_view({'get': 'minhas_reservas'}), 
         name='minhas-reservas'),
    path('reservas/como-anfitriao/', 
         views.ReservaViewSet.as_view({'get': 'como_anfitriao'}), 
         name='reservas-como-anfitriao'),
    path('avaliacoes/por-imovel/', 
         views.AvaliacaoViewSet.as_view({'get': 'por_imovel'}), 
         name='avaliacoes-por-imovel'),
]
