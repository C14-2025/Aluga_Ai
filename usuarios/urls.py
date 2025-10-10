from django.urls import path
from . import views

app_name = "usuarios"

urlpatterns = [
    path("cadastro/", views.cadastro_view, name="cadastro"),
    path("lista/", views.lista_usuarios, name="lista"),
]
