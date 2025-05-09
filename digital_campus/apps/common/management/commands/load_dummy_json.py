import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User

from apps.users.models import Profile
from apps.clubs.models import Club, ClubMembership
from apps.posts.models import Post
from apps.events.models import Event, EventOwnership, AttendanceRecord


class Command(BaseCommand):
    help = "Load dummy data from apps/common/fixtures/dummy_data.json"

    def handle(self, *args, **options):
        fixture_path = Path(__file__).resolve().parent.parent.parent / "fixtures" / "dummy_data.json"
        if not fixture_path.exists():
            self.stderr.write(f"✖ file not found: {fixture_path}")
            return

        raw = fixture_path.read_text(encoding="utf-8")
        data = json.loads(raw)
        self.stdout.write(f"Loaded JSON, {len(data)} records found.")

        # Keep track of instances by their model+pk
        users = {}
        profiles = {}
        clubs = {}
        posts = {}
        events = {}

        for obj in data:
            model = obj["model"]
            pk    = obj["pk"]
            fields= obj["fields"]

            if model == "auth.user":
                user, _ = User.objects.update_or_create(
                    pk=pk,
                    defaults={
                        "username": fields["username"],
                        "email":    fields["email"],
                        # if your fixtures include a hashed password:
                        "password": fields.get("password") or User.objects.make_random_password(),
                    }
                )
                users[pk] = user

            elif model == "users.profile":
                user = users[fields["user"]]
                prof, _ = Profile.objects.update_or_create(
                    pk=pk,
                    defaults={"user": user, "bio": fields.get("bio", "")}
                )
                profiles[pk] = prof

            elif model == "clubs.club":
                club, _ = Club.objects.update_or_create(
                    pk=pk,
                    defaults={
                        "name":        fields["name"],
                        "slug":        fields["slug"],
                        "description": fields.get("description", ""),
                        "is_featured": fields.get("is_featured", False),
                    }
                )
                clubs[pk] = club

            elif model == "clubs.clubmembership":
                prof = profiles[fields["profile"]]
                club = clubs[fields["club"]]
                ClubMembership.objects.update_or_create(
                    pk=pk,
                    defaults={
                        "profile": prof,
                        "club":    club,
                        "role":    fields.get("role", "member"),
                        "is_active": fields.get("is_active", True),
                    }
                )

            elif model == "posts.post":
                author = users[fields["author"]]
                post, _ = Post.objects.update_or_create(
                    pk=pk,
                    defaults={
                        "author":    author,
                        "title":     fields["title"],
                        "content":   fields["content"],
                        "date_posted": fields.get("date_posted", timezone.now()),
                    }
                )
                posts[pk] = post

            elif model == "events.event":
                creator = users[fields["created_by"]]
                club    = clubs.get(fields.get("club"))
                ev, _ = Event.objects.update_or_create(
                    pk=pk,
                    defaults={
                        "title":          fields["title"],
                        "description":    fields["description"],
                        "location":       fields["location"],
                        "starts_at":      fields["starts_at"],
                        "ends_at":        fields.get("ends_at"),
                        "created_by":     creator,
                        "club":           club,
                        "is_featured":    fields.get("is_featured", False),
                        "require_request":fields.get("require_request", False),
                    }
                )
                events[pk] = ev

            elif model == "events.eventownership":
                ev   = events[fields["event"]]
                club = clubs.get(fields.get("club"))
                user = users.get(fields.get("user"))
                EventOwnership.objects.update_or_create(
                    pk=pk,
                    defaults={"event": ev, "club": club, "user": user}
                )

            elif model == "events.attendancerecord":
                ev   = events[fields["event"]]
                user = users[fields["user"]]
                rec, _ = AttendanceRecord.objects.update_or_create(
                    pk=pk,
                    defaults={
                        "event":       ev,
                        "user":        user,
                        "status":      fields["status"],
                        "requested_at": fields.get("requested_at", timezone.now()),
                        "responded_at": fields.get("responded_at"),
                    }
                )

        self.stdout.write(self.style.SUCCESS("✅ Dummy JSON data loaded!"))
