# apps/events/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from digital_campus.storage_backends import MediaStorage  # S3 wrapper
from apps.clubs.models import Club
from apps.posts.models import validate_media_size
from apps.posts.models import ALLOWED_EXTS
from taggit.managers import TaggableManager


def _detect_media_type(filename: str) -> str:
    return "video" if filename.lower().endswith(("mp4", "mov", "avi", "mkv")) else "image"

# ────────────────
#   Event  model
# ────────────────
class Event(models.Model):
    title        = models.CharField(max_length=200)
    description  = models.TextField()
    location     = models.CharField(max_length=150)
    starts_at    = models.DateTimeField()
    duration        = models.DurationField(
        null = True,
        blank=True,
        help_text="Enter as [DD] [HH:[MM:[SS]]], e.g. 1 02:30 for 1 day 2h30m"
    )

    created_by   = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE
    )
    club         = models.ForeignKey(
        Club, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="events"
    )

    is_featured  = models.BooleanField(default=False)
    
    ## NEW ##
    require_request = models.BooleanField(
        default=False,
        help_text="If checked, users must request approval to attend."
    )

    requirements    = TaggableManager(blank=True, help_text="e.g. “CS only”, “19+”, “Alumni”")
    

    class Meta:
        ordering = ["-is_featured", "starts_at"]

    def __str__(self):
        return self.title

    def is_upcoming(self):
        return self.starts_at >= timezone.now()

    def get_absolute_url(self):
        return reverse("events:event-detail", kwargs={"pk": self.pk})
    
    ## NEW ##
    @property
    def attendees(self):
        # all attendance records with status attending
        return self.attendancerecord_set.filter(status=AttendanceRecord.STATUS_ATTENDING)
    

# ──────────────────────────────
# Attachment specifically for Event
# (same rules, different FK + path)
# ──────────────────────────────
class EventAttachment(models.Model):
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
        self.media_type = _detect_media_type(self.file.name)
        super().save(*args, **kwargs)


class AttendanceRecord(models.Model):
    STATUS_REQUESTED  = "requested"
    STATUS_ATTENDING = "attending"
    STATUS_CHOICES   = [
        (STATUS_REQUESTED,  "Requested to attend"),
        (STATUS_ATTENDING, "Attending"),
    ]

    event        = models.ForeignKey(Event, on_delete=models.CASCADE)
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES)
    requested_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("event", "user")

    def approve(self):
        self.status = self.STATUS_ATTENDING
        self.responded_at = timezone.now()
        self.save()

    def __str__(self):
        return f"{self.user} → {self.event} ({self.status})"