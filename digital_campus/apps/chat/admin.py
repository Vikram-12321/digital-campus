from django.contrib import admin
from .models import ChatRoom, ChatMessage, ChatAttachment

admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(ChatAttachment)