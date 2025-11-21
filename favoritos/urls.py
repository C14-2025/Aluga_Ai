from django.urls import path
from . import views

app_name = 'favoritos'

urlpatterns = [
    path('add/<int:propriedade_id>/', views.add_favorito, name='add'),
    path('remove/<int:propriedade_id>/', views.remove_favorito, name='remove'),
    path('list/', views.list_favoritos, name='list'),
]
