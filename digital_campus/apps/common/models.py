from django.db import models
from django.conf import settings
from django.db import models
from django.urls import reverse

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.conf import settings

class Course(models.Model):
    name = models.CharField(max_length=255)
    session = models.CharField(max_length=255)


    def __str__(self):
        return self.name

## Notifiation Model ##
class Notification(models.Model):
    recipient   = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='notifications', on_delete=models.CASCADE)
    actor       = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actor_notifications', on_delete=models.CASCADE)
    verb        = models.CharField(max_length=255)               # e.g. "sent you a follow request"
    target_ct   = models.ForeignKey(ContentType, null=True, blank=True, on_delete=models.CASCADE)
    target_id   = models.PositiveIntegerField(null=True, blank=True)
    target      = GenericForeignKey('target_ct', 'target_id')
    unread      = models.BooleanField(default=True)
    timestamp   = models.DateTimeField(auto_now_add=True)

    def get_target_url(self):
        if "follow" in self.verb and self.recipient.profile.is_private:
            return reverse('common:view-follow-requests')
        return reverse('common:notifications')