# forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.forms.widgets import ClearableFileInput

from .models import Post, Attachment

class MultiFileInput(ClearableFileInput):
    allow_multiple_selected = True                


class MultiFileField(forms.FileField):
    """
    Accepts *several* uploaded files instead of one.
    Runs the usual FileField validators on each item.
    """
    widget = MultiFileInput

    def clean(self, data, initial=None):
        # No files? Nothing to validate.
        if not data:
            return []

        # Browser may give us a single file => make it iterable
        if not isinstance(data, (list, tuple)):
            data = [data]

        cleaned_files, errors = [], []
        for f in data:
            try:
                cleaned_files.append(super().clean(f, initial))
            except ValidationError as e:
                errors.extend(e.error_list)

        if errors:
            raise ValidationError(errors)

        return cleaned_files


class PostForm(forms.ModelForm):
    """Simple edit form (no uploads)"""
    class Meta:
        model  = Post
        fields = ["title", "content"]


class PostWithFilesForm(PostForm):
    """Create/edit form that includes multi-file upload"""
    files = MultiFileField(
        required=False,
        validators=Attachment._meta.get_field("file").validators,
        help_text="Upload images/videos (each ≤ 50 MB).",
        widget=MultiFileInput(attrs={
            "multiple": True,
            "accept": ".jpg,.jpeg,.png,.gif,.mp4,.mov,.avi,.mkv",
        }),
    )

