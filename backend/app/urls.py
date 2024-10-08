from django.urls import path
from . import views 

urlpatterns = [
    path('example/', views.example_view, name='example_view'),
    path('all_models/', views.all_models, name='all_models'),
    path('models_info/', views.models_info, name='models_info'),
    path('chat/<int:chat_id>/', views.get_chat, name='get_chat'),
    path('chats/', views.get_chats, name='get_chats'),
    path('create_chat/', views.create_chat, name='create_chat'),
    path('chat/<int:chat_id>/get_ai_response/', views.ai_response, name='get_ai_response'),
]