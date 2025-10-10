from django.urls import path
from . import views

app_name = "avaliacoes"

urlpatterns = [
    path("nova/<int:prop_id>/", views.nova_avaliacao, name="nova"),
]
