# apps/users/models.py  (or wherever your Profile model lives)

from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default="profile_pics/default.jpg", upload_to="profile_pics")
    bio = models.TextField(max_length=500, blank=True)
    is_private = models.BooleanField(default=False)

    current_courses  = models.ManyToManyField("common.Course", related_name="enrolled_students", blank=True)
    past_courses     = models.ManyToManyField("common.Course", related_name="former_students", blank=True)

    # ――― SINGLE asymmetric M2M  (reverse manager is `followers`)
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True,
    )

    # follow-request tracking (keep as-is; still separate tables)
    follow_requests      = models.ManyToManyField("self", related_name="requested_follows", symmetrical=False, blank=True)
    following_requests   = models.ManyToManyField("self", related_name="pending_follow_requests", symmetrical=False, blank=True)

    group_channels = models.ManyToManyField("chat.GroupChannel", related_name="channel_members", blank=True)

    # -------------- utility methods --------------- #
    def clubs(self):
        return self.clubs_joined.filter(clubmembership__is_active=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def club_membership_records(self):
        return self.club_membership_set.all()

    @property
    def unread_notification_count(self):
        return self.notifications.filter(unread=True).count()
