"""
apps/events/models.py

Defines the core models for the events system:
- Event: base model for user- or club-hosted events
- EventOwnership: links events to either a user or a club
- EventAttachment: media files (images/videos) attached to events
- AttendanceRecord: links users to events with status (requested/attending)

Also includes utility logic like automatic media-type detection.

Author: Vikram Bhojanala
Last updated: 2025-05-02
"""

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError
from taggit.models import TagBase, GenericTaggedItemBase

from digital_campus.storage_backends import MediaStorage
from apps.clubs.models import Club
from apps.posts.models import validate_media_size, ALLOWED_EXTS
from taggit.managers import TaggableManager


def _detect_media_type(filename: str) -> str:
    """
    Determines the media type (image or video) based on the file extension.
    """
    return "video" if filename.lower().endswith(("mp4", "mov", "avi", "mkv")) else "image"

class TaggedEventTag(GenericTaggedItemBase):
    tag = models.ForeignKey(
        'events.EventTag',
        related_name="tagged_items",
        on_delete=models.CASCADE
    )

class EventTag(TagBase):
    class Meta:
        verbose_name = "Event Tag"
        verbose_name_plural = "Event Tags"

# ————————————————————————————————
# Event Model
# ————————————————————————————————
class Event(models.Model):
    """
    Represents an event, optionally hosted by a club or user.
    Can include location, time, duration, attendance control, and tags.
    """
    title        = models.CharField(max_length=200)
    description  = models.TextField()
    location     = models.CharField(max_length=150)
    starts_at    = models.DateTimeField()
    ends_at      = models.DateTimeField(null=True, blank=True)
    duration     = models.DurationField(
        null=True,
        blank=True,
        help_text="Enter as [DD] [HH:[MM:[SS]]], e.g. 1 02:30 for 1 day 2h30m"
    )

    created_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    club         = models.ForeignKey(
        Club, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name="events"
    )

    is_featured = models.BooleanField(default=False)

    require_request = models.BooleanField(
        default=False,
        help_text="If checked, users must request approval to attend."
    )

    requirements = TaggableManager(
        blank=True,
        help_text='e.g. “CS only”, “19+”, “Alumni”'
    )

    tags = TaggableManager(
        through=TaggedEventTag,
        blank=True,
        help_text='Hashtag-like keywords, e.g. “free food”, “tech”, “career”'
    )

    class Meta:
        ordering = ["-is_featured", "starts_at"]

    def __str__(self):
        return f"{self.title} ({self.starts_at:%b %d, %Y})"

    def is_upcoming(self):
        """
        Returns True if the event is in the future.
        """
        return self.starts_at >= timezone.now()

    def get_absolute_url(self):
        return reverse("events:event-detail", kwargs={"pk": self.pk})

    @property
    def attendees(self):
        """
        Returns all users attending the event (not just requested).
        """
        return self.attendancerecord_set.filter(status=AttendanceRecord.STATUS_ATTENDING)

    @property
    def owner(self):
        """
        Returns the owner of the event (user or club).
        """
        if hasattr(self, "ownership"):
            return self.ownership.club or self.ownership.user
        return None


# ————————————————————————————————
# EventOwnership Model
# ————————————————————————————————
class EventOwnership(models.Model):
    """
    Represents ownership of an event by either a user or a club.
    Only one of (user or club) should be non-null.
    """
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name="ownership")
    club  = models.ForeignKey(Club, null=True, blank=True, on_delete=models.CASCADE, related_name="owned_events")
    user  = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="owned_events")

    def clean(self):
        if not self.club and not self.user:
            raise ValidationError("An owner must be either a user or a club.")
        if self.club and self.user:
            raise ValidationError("An event can be owned by either a user or a club, not both.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.club:
            return f"{self.event.title} (Club: {self.club.name})"
        if self.user:
            return f"{self.event.title} (User: {self.user.username})"
        return self.event.title


# ————————————————————————————————
# EventAttachment Model
# ————————————————————————————————
class EventAttachment(models.Model):
    """
    File attachments for an event, limited to images and videos.
    Validated and uploaded via S3 (MediaStorage).
    """
    EVENT_MEDIA_TYPES = (("image", "Image"), ("video", "Video"))

    event = models.ForeignKey(
        Event, related_name="attachments", on_delete=models.CASCADE
    )
    file = models.FileField(
        upload_to="events/%Y/%m/%d/attachments/",
        storage=MediaStorage(),
        validators=[FileExtensionValidator(ALLOWED_EXTS), validate_media_size],
    )
    media_type = models.CharField(
        max_length=5, choices=EVENT_MEDIA_TYPES, editable=False
    )

    def save(self, *args, **kwargs):
        # Automatically assign media type based on file extension
        self.media_type = _detect_media_type(self.file.name)
        super().save(*args, **kwargs)


# ————————————————————————————————
# AttendanceRecord Model
# ————————————————————————————————
class AttendanceRecord(models.Model):
    """
    Represents a user's attendance status for an event.
    Tracks both requested and confirmed attendance.
    """
    STATUS_REQUESTED = "requested"
    STATUS_ATTENDING = "attending"
    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested to attend"),
        (STATUS_ATTENDING, "Attending"),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user  = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("event", "user")

    def approve(self):
        """
        Marks the record as approved and sets the response timestamp.
        """
        self.status = self.STATUS_ATTENDING
        self.responded_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.user} → {self.event} ({self.status})"
