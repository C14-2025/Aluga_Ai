from django.urls import path
from . import views

app_name = "reservas"

urlpatterns = [
    path("nova/<int:prop_id>/", views.nova_reserva, name="nova"),
    path("minhas/", views.minhas_reservas, name="minhas"),
    path("recebidas/", views.solicitacoes_recebidas, name="recebidas"),
    path("<int:reserva_id>/<str:acao>/", views.reserva_acao, name="acao"),
]