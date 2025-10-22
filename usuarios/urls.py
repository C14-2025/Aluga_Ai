from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "usuarios"

urlpatterns = [
    path("cadastro/", views.cadastro_view, name="cadastro"),
    path("perfil/<int:pk>/", views.perfil_view, name="perfil"),

    path("login/", views.CustomLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]
