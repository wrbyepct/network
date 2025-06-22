"""Custom forms."""

from django import forms


class MultipleFileInput(forms.ClearableFileInput):
    """Cutstom file input to allow multiple select."""

    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    """
    A file field that supports multiple file uploads.

    Uses a custom widget and overrides clean() to handle lists of files.
    """

    def __init__(self, *args, **kwargs) -> None:
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        """Override .clean method to allow validating each value & allowed upload amount."""
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result
