"""
apps/events/forms.py

Defines form classes for event creation and editing, including file upload support.
Uses custom widgets to allow multiple media attachments, and customizes input fields
to match frontend expectations (e.g., datetime-local inputs).

Author: Your Name or Team
Last updated: 2025-05-02
"""

from django import forms
from django.forms.widgets import ClearableFileInput
from .models import EventAttachment, Event


# ————————————————————————————
# Custom File Input for Multiple Files
# ————————————————————————————
class MultiFileInput(ClearableFileInput):
    """
    Custom widget allowing users to select and upload multiple files.
    """
    allow_multiple_selected = True


# ————————————————————————————
# Event Form with File Upload Support
# ————————————————————————————
class EventWithFilesForm(forms.ModelForm):
    """
    Event form that includes support for multiple image/video file attachments.
    """
    files = forms.FileField(
        widget=MultiFileInput(attrs={
            "multiple": True,
            "accept": ".jpg,.jpeg,.png,.gif,.mp4,.mov,.avi,.mkv",
        }),
        required=False,
        validators=EventAttachment._meta.get_field("file").validators,
        help_text="Upload images/videos (each ≤ 50 MB)."
    )

    class Meta:
        model = Event
        fields = [
            "title", "description", "starts_at", "ends_at",
            "location", "require_request", "requirements"
        ]
        widgets = {
            "starts_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "ends_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "requirements": forms.TextInput(attrs={
                "placeholder": "Add tags separated by commas"
            }),
        }


# ————————————————————————————
# Basic Event Form (No File Upload)
# ————————————————————————————
class EventForm(forms.ModelForm):
    """
    Standard event form without file upload capability.
    Used where file attachments are not required.
    """

    class Meta:
        model = Event
        fields = [
            "title", "description", "starts_at", "ends_at",
            "location", "require_request", "requirements"
        ]
        widgets = {
            "starts_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "ends_at": forms.DateTimeInput(
                attrs={"type": "datetime-local"}, format="%Y-%m-%dT%H:%M"
            ),
            "requirements": forms.TextInput(attrs={
                "placeholder": "Add tags separated by commas"
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Formats initial datetime values for datetime-local input compatibility.
        """
        super().__init__(*args, **kwargs)
        for field_name in ["starts_at", "ends_at"]:
            if self.instance and getattr(self.instance, field_name):
                self.fields[field_name].initial = getattr(
                    self.instance, field_name
                ).strftime("%Y-%m-%dT%H:%M")
