"""
apps/common/context_processors.py

Custom context processors for global template access to:
- Featured events (up to 10 upcoming)
- Unread notifications (top 5 + count)

Ensure this module is added to TEMPLATES > 'OPTIONS' > 'context_processors' in settings.py.

Author: Your Name or Team
Last updated: 2025-05-02
"""

from django.utils import timezone
from django.http import HttpRequest
from apps.events.models import Event


def featured_events(request: HttpRequest) -> dict:
    """
    Adds up to 10 upcoming events to the template context, ordered by soonest.
    """
    events = (
        Event.objects
        .filter(starts_at__gte=timezone.now())
        .order_by('starts_at')[:10]
    )
    return {"featured_events": events}


def notifications(request: HttpRequest) -> dict:
    """
    Adds unread notifications and count to the template context for logged-in users.
    Provides:
        - notifications_unread_list: Top 5 unread notifications (latest first)
        - notifications_unread_count: Total unread count

    Returns an empty context if user is not authenticated.
    """
    if request.user.is_authenticated:
        unread_qs = (
            request.user.notifications
            .filter(unread=True)
            .order_by('-timestamp')
        )
        return {
            'notifications_unread_list': unread_qs[:5],
            'notifications_unread_count': unread_qs.count(),
        }
    return {}
