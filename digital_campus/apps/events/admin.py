from django.contrib import admin
from .models import Event, EventAttachment


class EventAttachmentInline(admin.StackedInline):
    model = EventAttachment
    extra = 1

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display  = ("title", "starts_at", "location", "club", "is_featured", "require_request")
    list_filter   = ("is_featured", "club", "require_request")
    search_fields = ("title", "description", "location")
    inlines       = [EventAttachmentInline]
    autocomplete_fields = ("club",)

