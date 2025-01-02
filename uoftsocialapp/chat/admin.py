from django.contrib import admin
from .models import GroupChannel, ChatRoom, ChatMessage, ChatAttachment

admin.site.register(GroupChannel)
admin.site.register(ChatRoom)
admin.site.register(ChatMessage)
admin.site.register(ChatAttachment)