# channels/urls.py
from django.urls import path
from .views import chat_room, file_upload

urlpatterns = [
    path('chat/<str:room_name>/', chat_room, name='chat-room'),
    path('chat/upload/', file_upload, name='chat-file-upload'),
]
