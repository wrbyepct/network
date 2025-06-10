"""Post forms."""

from django import forms

from .constants import ALLOWED_POST_IMAGE_NUM
from .models import Post, PostMedia
from .validators import validate_image_extension


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

    def _validate_file_num(self, values):
        if len(values) > ALLOWED_POST_IMAGE_NUM:
            msg = f"You can only upload up to {ALLOWED_POST_IMAGE_NUM} images"
            raise forms.ValidationError(msg)

    def clean(self, data, initial=None):
        """Override .clean method to allow validating each value & allowed upload amount."""
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            self._validate_file_num(data)  # Check allowed upload number first
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class PostForm(forms.ModelForm):
    """Form for create/edit form."""

    content = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "row": "4",
                "placeholder": "What's on your mind?",
            }
        ),
    )
    images = MultipleFileField(required=False, validators=[validate_image_extension])

    class Meta:
        model = Post
        fields = ["content"]

    def save_media(self, post):
        """Save media(images/vidoe) after validation if any."""
        images = self.cleaned_data.get("images")
        if images:
            PostMedia.objects.bulk_create(
                [
                    PostMedia(
                        post=post,
                        file=image,
                        type=PostMedia.MediaType.IMAGE,
                        order=index,
                    )
                    for index, image in enumerate(images, start=1)
                ]
            )
