"""
apps/common/models.py

Defines shared models used across the platform:
- Course: for academic tagging and autocomplete
- Notification: generic notification system with support for follow requests and content linking

Author: Your Name or Team
Last updated: 2025-05-02
"""

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


# ————————————————————————————————————
# Course Model (e.g., for user-tagged courses or filtering)
# ————————————————————————————————————
class Course(models.Model):
    name = models.CharField(max_length=255)
    session = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class NotificationType(models.TextChoices):
    FOLLOW_REQUEST = "FOLLOW_REQUEST", "has requested to follow you"
    FOLLOW = "FOLLOW", "started following you"
    ACCEPT_FOLLOW_REQUEST = "ACCEPT_FOLLOW_REQUEST", "accepted your follow request"
    EVENT_REQUEST = "EVENT_REQUEST", "requested to attend your event"
    EVENT_ACCEPT = "EVENT_ACCEPT", "accepted your event request"
    EVENT_ATTEND = "EVENT_ATTEND", "is attending your event"
    CLUB_JOIN_REQUEST = "CLUB_JOIN_REQUEST", "requested to join your club"
    CLUB_JOIN = "CLUB_JOIN", "joined your club"
    CLUB_JOIN_ACCEPT = "CLUB_JOIN_ACCEPT", "accepted your club join request"

# ————————————————————————————————————
# Notification Model
# ————————————————————————————————————
class Notification(models.Model):
    """
    Generic notification model supporting arbitrary linked content via
    Django's ContentType framework. Handles both direct actions (e.g., likes)
    and special flows like follow requests.
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notifications',
        on_delete=models.CASCADE
    )
    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='actor_notifications',
        on_delete=models.CASCADE
    )

    type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        null=True,     # <-- TEMP: allow null
        blank=True     # <-- TEMP: allow blank
    )

    # Generic relation to any model object (e.g., post, comment, etc.)
    target_ct = models.ForeignKey(
        ContentType,
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    target_id = models.PositiveIntegerField(null=True, blank=True)
    target = GenericForeignKey('target_ct', 'target_id')

    unread = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.actor} {self.verb} ({'unread' if self.unread else 'read'})"

    @property
    def verb(self):
        return NotificationType(self.type).label

    def get_target_url(self):
        if self.type == NotificationType.FOLLOW_REQUEST and getattr(self.recipient.profile, "is_private", False):
            return reverse("common:view-follow-requests")
        return reverse("common:notifications")
