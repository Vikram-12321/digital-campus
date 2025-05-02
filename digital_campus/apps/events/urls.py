from django.urls import path, include

from .views import (
    EventDetailView, EventDeleteView,
    EventFeed, toggle_feature, create_or_edit_event       
)
from apps.posts.views import (
    AttachmentDeleteView
    )

app_name = 'events'
urlpatterns = [
    path("events/",                    EventFeed.as_view(),   name="event-feed"),
    path("events/new/",                create_or_edit_event,  name="event-create"),
    path("events/<int:pk>/",           EventDetailView.as_view(),  name="event-detail"),
    path("events/<int:pk>/edit/",      create_or_edit_event,  name="event-update"),
    path("events/<int:pk>/delete/",    EventDeleteView.as_view(),  name="event-delete"),
    path("events/<int:pk>/feature/",   toggle_feature,             name="event-toggle-feature"),
    path("attachment/<int:pk>/delete/", AttachmentDeleteView.as_view(),
         name="attachment-delete"),


]