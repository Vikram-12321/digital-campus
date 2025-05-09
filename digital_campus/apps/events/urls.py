"""
events/urls.py

URL configuration for all event-related routes, including creation, detail,
editing, deletion, feature toggling, and attachment management.

This module also integrates attachment-related views from the posts app.

Author: Your Name or Team
Last updated: 2025-05-02
"""

from django.urls import path
from .views import (
    EventDetailView,
    EventDeleteView,
    EventFeed,
    toggle_feature,
    EventCreateUpdateView,
    attend_event,
    UserEventsView
)
from apps.posts.views import AttachmentDeleteView


app_name = "events"

urlpatterns = [
    # ——— Event Feed ———
    path("events/", EventFeed.as_view(), name="event-feed"),

    ## User Events
    path("my-events/", UserEventsView.as_view(), name="user-events"),

    # ——— Event Create & Update ———
    path("events/new/", EventCreateUpdateView.as_view(), name="event-create"),
    path("events/<int:pk>/edit/", EventCreateUpdateView.as_view(), name="event-update"),

    # ——— Event Detail & Delete ———
    path("events/<int:pk>/", EventDetailView.as_view(), name="event-detail"),
    path("events/<int:pk>/delete/", EventDeleteView.as_view(), name="event-delete"),

    # ——— Feature Toggle (Admin) ———
    path("events/<int:pk>/feature/", toggle_feature, name="event-toggle-feature"),

    # ——— Attachment Deletion (Shared w/ Posts) ———
    path("attachment/<int:pk>/delete/", AttachmentDeleteView.as_view(), name="attachment-delete"),

    # ——— Attend Event ———
    path('<int:event_id>/attend/', attend_event, name='attend-event')
]
