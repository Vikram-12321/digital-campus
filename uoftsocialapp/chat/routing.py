# chat/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # e.g. ws://127.0.0.1:8000/ws/chat/<room_name>/
    re_path(r'^ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
