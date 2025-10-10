from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "usuarios"

urlpatterns = [
    path("cadastro/", views.cadastro_view, name="cadastro"),
    path("perfil/<int:pk>/", views.perfil_view, name="perfil"),

    # autenticação
    path("login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(next_page="/"), name="logout"),
]
