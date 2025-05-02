from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Automatically creates a Profile when a new User is created"""
    if created:
        Profile.objects.get_or_create(user=instance)  # Safely handle duplicate signals

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """Ensures the Profile is saved when the User is saved"""
    instance.profile.save()  # Works thanks to related_name='profile'