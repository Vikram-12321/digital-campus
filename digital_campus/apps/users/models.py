from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    bio = models.TextField(max_length=500, blank=True)
    is_private = models.BooleanField(default=False)  # Public/Private Account
    current_courses = models.ManyToManyField(
        'common.Course', related_name='enrolled_students', blank=True
    )
    past_courses = models.ManyToManyField(
        'common.Course', related_name='former_students', blank=True
    )
    followers = models.ManyToManyField(
        'self', related_name='followed_by', symmetrical=False, blank=True
    )
    following = models.ManyToManyField(
        'self', related_name='follows', symmetrical=False, blank=True
    )
    follow_requests = models.ManyToManyField(
        'self', related_name='requested_follows', symmetrical=False, blank=True
    )
    following_requests = models.ManyToManyField(
        'self', related_name='pending_follow_requests', symmetrical=False, blank=True
    )
    group_channels = models.ManyToManyField(
        'chat.GroupChannel', related_name='channel_members', blank=True
    )

    # club_memberships = models.ManyToManyField(
    #     "clubs.Club",
    #     through="clubs.ClubMembership",
    #     related_name="profiles_in_club",
    #     blank=True,
    # )

    def clubs(self):
        """Return active Club objects this profile belongs to."""
        return self.clubs_joined.filter(
            clubmembership__is_active=True
        )

    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    @property
    def club_membership_records(self):
        return self.club_membership_set.all()
    
    @property
    def unread_notification_count(self):
        return self.notifications.filter(unread=True).count()


