from django.urls import path
from . import views

app_name = 'recomendacoes_ml'

urlpatterns = [
    path('predict_price/', views.PricePredictionView.as_view(), name='predict_price'),
    path('recommend/', views.RecommendationView.as_view(), name='recommend'),
    path('survey_recommend/', views.SurveyRecommendationView.as_view(), name='survey_recommend'),
    path('retrain/', views.RetrainView.as_view(), name='retrain'),
]
