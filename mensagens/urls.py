from django.urls import path
from . import views

app_name = 'mensagens'

urlpatterns = [
    path('', views.conversations_list, name='list'),
    path('start/<int:user_id>/<int:prop_id>/', views.start_conversation, name='start'),
    path('<int:pk>/', views.conversation_detail, name='detail'),
    path('api/<int:pk>/messages/', views.ajax_get_messages, name='api_messages'),
    path('api/<int:pk>/send/', views.ajax_send_message, name='api_send'),
]
