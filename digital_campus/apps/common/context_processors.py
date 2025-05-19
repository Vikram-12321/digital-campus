"""
apps/common/context_processors.py

Custom context processors for global template access to:
- Featured events (up to 10 upcoming)
- Unread notifications (top 5 + count)

Ensure this module is added to:
    TEMPLATES > 'OPTIONS' > 'context_processors' in settings.py

Author: Vikram Bhojanala
Last updated: 2025-05-09
"""

from django.utils import timezone
from django.http import HttpRequest
from typing import Dict, Any

from apps.events.models import Event
from apps.notifications.models import Notification


def featured_events(request: HttpRequest) -> Dict[str, Any]:
    """
    Adds up to 10 upcoming events to the template context, ordered by start time.
    """
    events = (
        Event.objects
        .filter(starts_at__gte=timezone.now())
        .order_by('starts_at')[:10]
    )
    return {"featured_events": events}


def notifications(request: HttpRequest) -> Dict[str, Any]:
    """
    Adds unread notifications and count to the template context for logged-in users.

    Provides:
        - notifications_unread_list: Top 5 unread notifications (most recent first)
        - notifications_unread_count: Total unread count

    Returns an empty context if user is not authenticated.
    """
    if not request.user.is_authenticated:
        return {}

    # Avoid multiple evaluations of the same QuerySet
    unread_qs = (
        Notification.objects
        .filter(recipient=request.user, unread=True)
        .order_by('-timestamp')
    )

    return {
        "notifications_unread_list": list(unread_qs[:5]),
        "notifications_unread_count": unread_qs.count(),
    }
