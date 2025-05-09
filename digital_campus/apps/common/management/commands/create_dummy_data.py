# apps/common/management/commands/create_dummy_data.py

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction
import random

from apps.users.models import Profile
from apps.clubs.models import Club, ClubMembership
from apps.posts.models import Post
from apps.events.models import Event, EventOwnership, AttendanceRecord

class Command(BaseCommand):
    help = "Create dummy users, clubs, posts, events, and attendance records"

    def handle(self, *args, **options):
        with transaction.atomic():
            # 1) Users & Profiles
            users = []
            for i in range(10):
                username = f"user{i}"
                email = f"user{i}@example.com"
                u, created = User.objects.get_or_create(
                    username=username,
                    defaults={'email': email}
                )
                # Create or ensure Profile exists
                Profile.objects.get_or_create(
                    user=u,
                    defaults={'bio': f'This is bio of {username}'}
                )
                users.append(u)

            # 2) Clubs & Memberships
            clubs = []
            for i in range(5):
                name = f"Club {i}"
                slug = f"club-{i}"
                c, _ = Club.objects.get_or_create(
                    slug=slug,
                    defaults={'name': name, 'description': f'This is {name}'}
                )
                clubs.append(c)
                # Assign one random owner
                owner = random.choice(users)
                ClubMembership.objects.get_or_create(
                    profile=owner.profile,
                    club=c,
                    defaults={'role': 'owner'}
                )
                # Assign up to 3 other members
                others = [u for u in users if u != owner]
                k = min(len(others), 3)
                if k > 0:
                    for m in random.sample(others, k):
                        ClubMembership.objects.get_or_create(
                            profile=m.profile,
                            club=c,
                            defaults={'role': 'member'}
                        )

            # 3) Posts
            posts = []
            for i in range(15):
                author = random.choice(users)
                p, _ = Post.objects.get_or_create(
                    title=f"Post Title {i}",
                    author=author,
                    defaults={'content': 'Lorem ipsum dolor sit amet, ' * 5}
                )
                posts.append(p)

            # 4) Events
            events = []
            # Club-hosted events
            for c in clubs:
                for j in range(2):
                    start = timezone.now() + timezone.timedelta(days=random.randint(-5, 10))
                    e, _ = Event.objects.get_or_create(
                        title=f"{c.name} Event {j}",
                        club=c,
                        defaults={
                            'description': 'An event description ' * 3,
                            'location': 'Some Venue',
                            'starts_at': start,
                            'ends_at': start + timezone.timedelta(hours=2),
                            'created_by': random.choice(users),
                        }
                    )
                    EventOwnership.objects.get_or_create(event=e, club=c)
                    # Add some tags if taggit used
                    try:
                        e.requirements.add('TagA', 'TagB')
                    except Exception:
                        pass
                    events.append(e)
            # User-hosted events
            for i in range(3):
                author = random.choice(users)
                start = timezone.now() + timezone.timedelta(days=random.randint(-3, 7))
                e, _ = Event.objects.get_or_create(
                    title=f"User {author.username} Event {i}",
                    created_by=author,
                    defaults={
                        'description': 'User-hosted event desc',
                        'location': 'Home Base',
                        'starts_at': start,
                        'ends_at': start + timezone.timedelta(hours=1),
                    }
                )
                EventOwnership.objects.get_or_create(event=e, user=author)
                events.append(e)

            # 5) AttendanceRecords
            for e in events:
                # random number of attendees up to total users
                max_att = len(users)
                num_att = random.randint(0, max_att)
                if num_att > 0:
                    for u in random.sample(users, num_att):
                        status = random.choice([
                            AttendanceRecord.STATUS_REQUESTED,
                            AttendanceRecord.STATUS_ATTENDING
                        ])
                        rec, _ = AttendanceRecord.objects.get_or_create(
                            event=e,
                            user=u,
                            defaults={'status': status}
                        )
                        if status == AttendanceRecord.STATUS_ATTENDING:
                            rec.responded_at = timezone.now()
                            rec.save()

            self.stdout.write(self.style.SUCCESS("Dummy data created successfully!"))
