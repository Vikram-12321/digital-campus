# apps/clubs/models.py

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from apps.users.models import Profile  # ← we’re using Profile as the member

class Club(models.Model):
    name        = models.CharField(max_length=120, unique=True)
    slug        = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    banner      = models.ImageField(upload_to="club_banners/", blank=True)
    avatar      = models.ImageField(upload_to="club_avatars/", blank=True)

    members = models.ManyToManyField(
        Profile,
        through="ClubMembership",
        through_fields=("club", "profile"),
        related_name="clubs_joined",
        blank=True
    )

    created_at  = models.DateTimeField(auto_now_add=True)
    is_featured = models.BooleanField(default=False)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("clubs:detail", args=[self.slug])


class ClubMembership(models.Model):
    ROLE_CHOICES = [
        ("owner",     "Owner"),
        ("moderator", "Moderator"),
        ("member",    "Member"),
    ]

    profile   = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="club_membership_set"
    )
    club      = models.ForeignKey(Club, on_delete=models.CASCADE)
    role      = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("profile", "club")
        ordering        = ["club", "role", "-joined_at"]

    def __str__(self):
        return f"{self.profile.user.username} in {self.club.name} as {self.role}"

