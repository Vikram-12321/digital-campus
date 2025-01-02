# channels/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, ChatMessage, ChatAttachment

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Called when the websocket is handshaking as part of initial connection.
        """
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        """
        Called when the websocket closes.
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """
        Called when a message is received from the WebSocket.
        """
        data = json.loads(text_data)
        message = data.get('message')
        message_type = data.get('type', 'text')  # "text", "typing", "upload"

        # Handle "user is typing..."
        if message_type == 'typing':
            # broadcast to group that user is typing
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_typing',
                    'user': self.scope['user'].username,
                }
            )
            return

        # Otherwise handle text or file messages
        await self.save_message(self.scope['user'].id, self.room_name, message)
        
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': self.scope['user'].username,
            }
        )

    async def chat_message(self, event):
        """
        Receive message from room group, then send to WebSocket.
        """
        message = event['message']
        username = event['username']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'type': 'text'
        }))

    async def chat_typing(self, event):
        """
        Called when a user is typing.
        """
        user = event['user']
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user': user
        }))

    @database_sync_to_async
    def save_message(self, user_id, room_name, message):
        user = User.objects.get(pk=user_id)
        room, created = ChatRoom.objects.get_or_create(name=room_name)
        # Make sure user is a participant
        room.participants.add(user)  # If you want them auto-added

        return ChatMessage.objects.create(room=room, user=user, content=message)
