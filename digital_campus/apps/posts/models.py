# apps/posts/models.py
from django.db import models
from django.conf import settings
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from taggit.managers import TaggableManager  # add this if not already there
from taggit.models import TagBase, GenericTaggedItemBase

from apps.users.models import Profile
from apps.clubs.models import Club
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


class TaggedPostTag(GenericTaggedItemBase):
    tag = models.ForeignKey(
        'posts.PostTag',
        related_name="tagged_items",
        on_delete=models.CASCADE
    )

class PostTag(TagBase):
    class Meta:
        verbose_name = "Post Tag"
        verbose_name_plural = "Post Tags"

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

    tags = TaggableManager(
        through=TaggedPostTag,
        blank=True,
        help_text='Hashtag-style labels for discovery and algorithmic grouping.'
    )

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("posts:post-detail", kwargs={"pk": self.pk})
    
    def like_count(self):
        return self.likes.count()

    def comment_count(self):
        return self.comments.count()
    
    @property
    def owner(self):
        if hasattr(self, "ownership"):
            return self.ownership.club or self.ownership.user
        return None
    
def validate_video_size(l):
    None

class PostOwnership(models.Model):
    post = models.OneToOneField("Post", on_delete=models.CASCADE, related_name="ownership")
    club = models.ForeignKey(Club, null=True, blank=True, on_delete=models.CASCADE, related_name="owned_posts")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE, related_name="owned_posts")

    def clean(self):
        if not self.club and not self.user:
            raise ValidationError("An owner must be either a user or a club.")
        if self.club and self.user:
            raise ValidationError("A post can be owned by either a user or a club, not both.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        if self.club:
            return f"{self.post.title} (Club: {self.club.name})"
        if self.user:
            return f"{self.post.title} (User: {self.user.username})"
        return self.post.title
    

# ────────────────
#   Post Like model
# ────────────────
class PostLike(models.Model):
    post = models.ForeignKey(Post, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('post', 'user')


# ────────────────
#   Post Comment model
# ────────────────
class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)