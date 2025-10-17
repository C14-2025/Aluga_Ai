from django.urls import path
from . import views

app_name = "propriedades"

urlpatterns = [
    path("", views.lista_propriedades, name="lista"),
    path("nova/", views.criar_propriedade, name="nova"),
    path("<int:pk>/", views.detalhe_propriedade, name="detalhe"),
]
