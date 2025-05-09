# apps/clubs/models.py

from django.utils import timezone
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from apps.users.models import Profile  # ← we’re using Profile as the member
from django.utils.text import slugify

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
    require_request = models.BooleanField(default=False, help_text="Require admin approval to join this club.")

    # Ownership of events via EventOwnership
    events_owned = models.ManyToManyField(
        'events.Event',
        through='events.EventOwnership',
        through_fields=('club', 'event'),
        related_name='owning_clubs',
        blank=True
    )

    posts_owned = models.ManyToManyField(
        'posts.Post',
        through='posts.PostOwnership',
        through_fields=('club', 'post'),
        related_name='owning_clubs',
        blank=True
    )


    creator = models.ForeignKey(
        "users.Profile",  # or settings.AUTH_USER_MODEL if you're using User directly
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="clubs_created"
    )

    class Meta:
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name)
            slug = base_slug
            counter = 1
            while Club.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("clubs:club-detail", args=[self.slug])
    
    @property
    def active_memberships(self):
        return self.club_membership_set.filter(status="member")
    
    @property
    def members(self):
        return self.club_membership_set.filter(role="member").select_related("profile__user")
    

class ClubMembership(models.Model):
    # Membership status logic
    STATUS_REQUESTED = "requested"
    STATUS_MEMBER    = "member"

    STATUS_CHOICES = [
        (STATUS_REQUESTED, "Requested"),
        (STATUS_MEMBER, "Member"),
    ]

    # Role logic
    ROLE_CHOICES = [
        ("owner",     "Owner"),
        ("moderator", "Moderator"),
        ("member",    "Member"),
    ]

    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="club_membership_set"
    )
    club = models.ForeignKey(
        Club,
        on_delete=models.CASCADE,
        related_name="club_membership_set"
    )

    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default="member"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_MEMBER  # will be updated automatically if requests are required
    )

    joined_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("profile", "club")
        ordering = ["club", "role", "-joined_at"]

    def approve(self):
        self.status = self.STATUS_MEMBER
        self.responded_at = timezone.now()
        self.save()

    def is_owner(self):
        return self.role == "owner"

    def __str__(self):
        return f"{self.profile.user.username} in {self.club.name} as {self.role} ({self.status})"


