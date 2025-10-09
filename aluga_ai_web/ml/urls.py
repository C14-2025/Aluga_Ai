from django.urls import path
from .views import PricePredictionView

urlpatterns = [
    path('price/', PricePredictionView.as_view(), name='ml-price'),
]

