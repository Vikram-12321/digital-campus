# chat/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from .models import ChatRoom, ChatMessage, ChatAttachment


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            return await self.close()

        self.room_name      = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group     = f"chat_{self.room_name}"
        self.room           = await self.get_room(self.room_name)

        if not await self.is_participant(self.room, user):
            return await self.close()

        await self.channel_layer.group_add(self.room_group, self.channel_name)
        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message')
        message_type = data.get('type', 'text')

        if message_type == 'typing':
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_typing',
                    'user': self.scope['user'].username,
                }
            )
            return

        # Save the message
        saved_message = await self.save_message(self.scope['user'].id, self.room_name, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': saved_message.content,
                'username': saved_message.user.username,
                # optionally pass an ID or timestamp for the UI
                'timestamp': str(saved_message.timestamp),
                # pass user’s profile pic if you have it
                'profile_pic_url': saved_message.user.profile.profile_pic.url 
                    if hasattr(saved_message.user, 'profile') and saved_message.user.profile.profile_pic 
                    else '', 
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'type': 'text',
            'timestamp': event['timestamp'],
            'profile_pic_url': event.get('profile_pic_url', ''),
        }))

    async def chat_typing(self, event):
        user = event['user']
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': user
        }))

    @database_sync_to_async
    def get_room(self, room_name):
        return ChatRoom.objects.get(name=room_name)

    @database_sync_to_async
    def is_participant(self, room, user):
        return user in room.participants.all()

    @database_sync_to_async
    def save_message(self, user_id, room_name, message):
        user = User.objects.get(pk=user_id)
        room = ChatRoom.objects.get(name=room_name)
        return ChatMessage.objects.create(room=room, user=user, content=message)
