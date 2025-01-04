from django.db import models

class GroupChannel(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name
    
# channels/models.py
from django.db import models
from django.contrib.auth.models import User
from PIL import Image
import os

def chat_attachment_path(instance, filename):
    """
    Dynamically build path for chat attachments, e.g. chat_attachments/room_<room_id>/<filename>
    """
    return f"chat_attachments/room_{instance.chat_message.room.id}/{filename}"

class ChatRoom(models.Model):
    """
    ChatRoom can be a group chat or a direct 1:1 private room.
    """
    name = models.CharField(max_length=255, unique=True)
    participants = models.ManyToManyField(User, blank=True, related_name='chat_rooms')
    is_private = models.BooleanField(default=False)

    # Optional group icon
    room_icon = models.ImageField(upload_to='chat_room_icons/', null=True, blank=True)

    def __str__(self):
        room_type = "Private DM" if self.is_private else "Group Chat"
        return f"{self.name} ({room_type})"

class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} in {self.room.name}: {self.content[:20]}"

class ChatAttachment(models.Model):
    """
    Store original file and possibly a thumbnail for images/videos.
    """
    chat_message = models.ForeignKey(ChatMessage, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to=chat_attachment_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # We'll store a thumbnail if it's an image. (Optional)
    thumbnail = models.ImageField(upload_to='chat_attachments/thumbnails/', null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Override save to create a thumbnail if it's an image.
        """
        super().save(*args, **kwargs)
        
        # Generate thumbnail if it's an image
        if self.file and self.file.name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
            self.generate_thumbnail()

    def generate_thumbnail(self):
        """
        Create a thumbnail for the uploaded image.
        """
        try:
            img = Image.open(self.file)
            img.thumbnail((300, 300))  # max width/height
            thumbnail_name, thumbnail_extension = os.path.splitext(self.file.name)
            thumbnail_extension = thumbnail_extension.lower()
            thumbnail_filename = thumbnail_name + '_thumb' + thumbnail_extension

            # Save to in-memory
            from io import BytesIO
            thumb_io = BytesIO()
            img.save(thumb_io, format=img.format)
            
            # Save the thumbnail to the field
            self.thumbnail.save(thumbnail_filename, content=thumb_io, save=False)
            super().save()
        except Exception as e:
            print("Error generating thumbnail:", e)


