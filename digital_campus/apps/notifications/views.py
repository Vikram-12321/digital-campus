"""
apps/notifications/views.py

Contains shared views for the Digital Campus project, including:
- User notifications (list, dismiss)

Integrates home feed scoring (recency, relevance) via modular imports.

Author: Vikram Bhojanala  
Last updated: 2025-05-09
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse

from .models import Notification


# ————————————————————————————————————
# Notifications
# ————————————————————————————————————
@login_required
def notifications_list(request: HttpRequest) -> HttpResponse:
    """
    Show all of the user's notifications, most recent first.
    Marks all unread notifications as read in one bulk update.
    """
    Notification.objects.filter(recipient=request.user, unread=True).update(unread=False)

    notifications = (
        Notification.objects
        .with_all_related()
        .filter(recipient=request.user)
        .order_by('-timestamp')
    )

    return render(request, "notifications/list.html", {
        "notifications": notifications
    })


@login_required
def dismiss_notification(request: HttpRequest, pk: int) -> HttpResponse:
    """
    Deletes a notification by primary key.
    Redirects to the referring page or the notifications page.
    """
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.delete()
    return redirect(request.META.get('HTTP_REFERER', 'notifications:notifications'))
