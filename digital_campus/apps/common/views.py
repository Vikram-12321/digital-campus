"""
apps/common/views.py

Contains shared views for the Digital Campus project, including:
- Static pages (About, Account)
- Autocomplete for course selection
- User notifications (list, dismiss)

Also integrates home feed scoring algorithms (recency, relevance).

Author: Your Name or Team
Last updated: 2025-05-02
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from dal import autocomplete
from itertools import chain

# Scoring functions for personalized content
from .home_algorithim import recency_score, relevance_score, ALPHA, BETA

# Models
from .models import Course, Notification
from apps.posts.models import Post
from apps.events.models import Event


# ————————————————————————————————————
# Static Pages
# ————————————————————————————————————
def about(request):
    """Render the About page."""
    return render(request, 'digital_campus/about.html')


def account(request):
    """Render the Account page."""
    return render(request, 'digital_campus/account.html')


# ————————————————————————————————————
# Autocomplete
# ————————————————————————————————————
class CourseAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for course selection using django-autocomplete-light.
    Returns filtered course queryset based on user input.
    """

    def get_queryset(self):
        # Ensure only authenticated users can trigger autocomplete
        if not self.request.user.is_authenticated:
            return Course.objects.none()

        qs = Course.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


# ————————————————————————————————————
# Notifications
# ————————————————————————————————————
@login_required
def notifications_list(request):
    """
    List all notifications for the logged-in user.
    Marks all unread notifications as read.
    """
    qs = request.user.notifications.order_by('-timestamp')
    qs.filter(unread=True).update(unread=False)
    return render(request, 'digital_campus/notifications/list.html', {'notifications': qs})


@login_required
def dismiss_notification(request, pk):
    """
    Dismiss (delete) a specific notification by primary key.
    Redirects back to the referring page or fallback to notifications list.
    """
    n = get_object_or_404(Notification, pk=pk, recipient=request.user)
    n.delete()
    return redirect(request.META.get('HTTP_REFERER', 'common:notifications'))
