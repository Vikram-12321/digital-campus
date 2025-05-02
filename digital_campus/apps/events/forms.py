from django import forms
from django.forms.widgets import ClearableFileInput
from .models import EventAttachment, Event

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True                

class EventWithFilesForm(forms.ModelForm):
    files = forms.FileField(
        widget=MultiFileInput(attrs={
            "multiple": True,
            "accept": ".jpg,.jpeg,.png,.gif,.mp4,.mov,.avi,.mkv",
        }),
        required=False,
        validators=EventAttachment._meta.get_field("file").validators,
        help_text="Upload images/videos (each ≤ 50 MB).",
    )

    class Meta:
        model  = Event
        fields = ["title", "description", "location", "starts_at", "club"]

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ["title", "description", "starts_at", "location", "duration", "require_request", "requirements"]
        widgets = {
            # taggit will render a comma-separated text input by default
            "requirements": forms.TextInput(attrs={"placeholder": "Add tags separated by commas"})
        }