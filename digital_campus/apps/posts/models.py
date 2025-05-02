# apps/posts/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone

from digital_campus.storage_backends import MediaStorage  # S3 wrapper


# ───────────────────────────
# Shared helpers / validators
# ───────────────────────────
ALLOWED_EXTS = ["jpg", "jpeg", "png", "gif", "mp4", "mov", "avi", "mkv"]


def validate_media_size(file):
    limit_mb = 50
    if file.size > limit_mb * 1024 * 1024:
        raise ValidationError(f"File too large (> {limit_mb} MB)")

def _detect_media_type(filename: str) -> str:
    return "video" if filename.lower().endswith(("mp4", "mov", "avi", "mkv")) else "image"

# ───────────────────────────
# Attachment for regular Post
# ───────────────────────────
class Attachment(models.Model):
    POST_MEDIA_TYPES = (("image", "Image"), ("video", "Video"))

    post = models.ForeignKey(
        "Post", related_name="attachments", on_delete=models.CASCADE
    )
    file = models.FileField(
        upload_to="posts/%Y/%m/%d/attachments/",
        storage=MediaStorage(),
        validators=[FileExtensionValidator(ALLOWED_EXTS), validate_media_size],
    )
    media_type = models.CharField(
        max_length=5, choices=POST_MEDIA_TYPES, editable=False
    )

    def save(self, *args, **kwargs):
        self.media_type = _detect_media_type(self.file.name)
        super().save(*args, **kwargs)


# ────────────────
#   Post model
# ────────────────
class Post(models.Model):
    title       = models.CharField(max_length=200)
    content     = models.TextField()
    author      = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_posted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:post-detail", kwargs={"pk": self.pk})
    
def validate_video_size(l):
    None