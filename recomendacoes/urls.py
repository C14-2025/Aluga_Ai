from django.urls import path
from . import views

app_name = "recomendacoes"

urlpatterns = [
    path("", views.index, name="index"),
    path("lista/", views.lista_recomendacoes, name="lista"),
]
