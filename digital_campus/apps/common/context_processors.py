# apps/common/context_processors.py
from django.utils import timezone
from apps.events.models import Event

def featured_events(request):
    """Up to 10 upcoming events, earliest first."""
    events = (Event.objects
                    .filter(starts_at__gte=timezone.now())   # ← starts_at
                    .order_by('starts_at')[:10])
    return {"featured_events": events}

def notifications(request):
    """
    Inject the current user’s top-5 unread notifications
    and their total unread count into every template.
    """
    if request.user.is_authenticated:
        # Get all unread, newest first
        unread_qs = request.user.notifications.filter(unread=True).order_by('-timestamp')
        return {
            'notifications_unread_list': unread_qs[:5],
            'notifications_unread_count': unread_qs.count(),
        }
    return {}    
