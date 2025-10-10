from django.urls import path
from .ml.views import PricePredictionView

urlpatterns = [
    path('price/', PricePredictionView.as_view(), name='ml-price'),
]

