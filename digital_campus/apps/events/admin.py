"""
apps/events/admin.py

Registers the Event and EventAttachment models with the Django admin interface.
Includes inline support for attachments and admin customization for filtering,
searching, and editing events.

Author: Your Name or Team
Last updated: 2025-05-02
"""

from django.contrib import admin
from .models import Event, EventAttachment


class EventAttachmentInline(admin.StackedInline):
    """
    Allows inline upload and management of attachments within an Event admin form.
    """
    model = EventAttachment
    extra = 1  # Show one empty slot by default


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    """
    Admin configuration for the Event model.
    Includes filtering, searching, and inline attachments.
    """
    list_display = (
        "title", "starts_at", "location", "club", "is_featured", "require_request"
    )
    list_filter = ("is_featured", "club", "require_request")
    search_fields = ("title", "description", "location")
    inlines = [EventAttachmentInline]
    autocomplete_fields = ("club",)
