# channels/urls.py
from django.urls import path
from .views import chat_room, file_upload
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('chat/<str:room_name>/', chat_room, name='chat-room'),
    path('chat/upload/', file_upload, name='chat-file-upload'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
