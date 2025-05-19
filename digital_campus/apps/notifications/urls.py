"""
apps/notifications/urls.py

URL configuration for the `notifications` app, handling:

- Notifications

Author: Vikram Bhojanala
Last updated: 2025-05-09
"""

from django.urls import path

# Core Views
from .views import (
    notifications_list,
    dismiss_notification,
)

app_name = "notifications"

urlpatterns = [
    # ——— Notifications ———
    path("notifications/", notifications_list, name="notifications"),
    path("notifications/dismiss/<int:pk>/", dismiss_notification, name="dismiss-notification"),

]
