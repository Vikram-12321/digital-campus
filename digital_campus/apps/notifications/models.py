"""
apps/notifications/models.py

Defines shared models used across the platform:
- Notification: generic notification system with support for follow requests and content linking

Author: Vikram Bhojanala
Last updated: 2025-05-02
"""

## Models Imports
from django.db import models
from apps.clubs.models import Club
from apps.events.models import Event
from django.db.models import Prefetch

## Utils (Django)
from django.conf import settings
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

## Helpers
from apps.notifications.utils.notifications import NotificationType

# ------------------------------------------------------------------
# QuerySet & Manager with the one-liner prefetch rule
# ------------------------------------------------------------------
from django.db.models import Prefetch

class NotificationQuerySet(models.QuerySet):
    def with_all_related(self):
        """
        Loads actor + recipient in one JOIN
        and fetches Event / Club targets with two
        separate prefetches that use UNIQUE to_attr names.
        """
        return (
            self
            .select_related("actor", "recipient")
            .prefetch_related(
                Prefetch(
                    "target",
                    queryset=Event.objects.only("id", "title"),
                    to_attr="event_target",        # ← unique
                ),
                Prefetch(
                    "target",
                    queryset=Club.objects.only("id", "name"),
                    to_attr="club_target",         # ← unique
                ),
            )
        )


class NotificationManager(models.Manager):
    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    # convenience alias
    def with_all_related(self):
        return self.get_queryset().with_all_related()

# ------------------------------------------------------------------
# Notification model
# ------------------------------------------------------------------
class Notification(models.Model):
    objects   = NotificationManager()

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name="notifications")
    actor     = models.ForeignKey(settings.AUTH_USER_MODEL,
                                  on_delete=models.CASCADE,
                                  related_name="actor_notifications")

    notification_type      = models.CharField(max_length=50,
                                choices=NotificationType.choices, 
                                editable=False)

    # Generic target (post, club, event …)
    target_ct = models.ForeignKey(ContentType, 
                                  on_delete=models.CASCADE
                                  )
    
    target_id = models.PositiveIntegerField()
    
    target    = GenericForeignKey("target_ct", "target_id")

    unread    = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    # ------------ Display helpers ---------------------------------
    def __str__(self):
        return f"Notification<{self.notification_type}> from {self.actor} to {self.recipient}"


    @property
    def verb(self):
        """
        Human-readable sentence, e.g.
        'Vikram has joined AI Club'.
        """
        return NotificationType.get_dynamic_verb(self.notification_type, actor=self.actor, target=self.target)

    def get_target_url(self):
        if (self.notification_type == NotificationType.FOLLOW_REQUEST
                and getattr(self.recipient.profile, "is_private", False)):
            return reverse("connections:view-follow-requests")
        return reverse("notifications:notifications")

    # ------------ Factory method ----------------------------------
    @classmethod
    def create_notification(cls, *, recipient, actor,
                            notification_type, target=None):
        """
        Single entry-point so calling code never worries about
        verb building or GFK plumbing.
        """
        target_ct = ContentType.objects.get_for_model(target) if target else None
        target_id = getattr(target, "id", None)

        return cls.objects.create(
            recipient    = recipient,
            actor        = actor,
            notification_type         = notification_type,
            target_ct    = target_ct,
            target_id    = target_id,
        )
