from django.urls import path
from . import views

app_name = "recomendacoes"

urlpatterns = [
    path("", views.index, name="index"),
]
