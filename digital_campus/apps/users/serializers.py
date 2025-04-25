# users/serializer.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile  # if you have a separate Profile model

class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['bio', 'is_private', 'current_courses', 'past_courses', 'followers', 
                  'following', 'follow_requests', 'following_requests', 'group_channels']

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'image', 'profile']

    def get_image(self, obj):
        try:
            return obj.profile.image.url
        except AttributeError:
            return None
