# users/serializer.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Profile  # if you have a separate Profile model

class UserSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['username', 'email', 'image']

    def get_image(self, obj):
        # If you have a OneToOne relation between User and Profile
        try:
            return obj.profile.image.url
        except:
            return None
