from django.contrib import admin
from .models import Post, Attachment

admin.site.register(Post)
admin.site.register(Attachment)