"""Post forms."""

from django import forms
from django.db.models import Max

from .constants import ALLOWED_POST_IMAGE_NUM, ALLOWED_POST_VIDEO_NUM
from .models import Post, PostMedia
from .validators import validate_image_extension, validate_video_extension


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
    video = forms.FileField(required=False, validators=[validate_video_extension])

    class Meta:
        model = Post
        fields = ["content"]

    def save_media(self, post):
        """Save media(images/vidoe) after validation if any."""
        images = self.cleaned_data.get("images")
        video = self.cleaned_data.get("video")
        if images:
            max_order = self._get_max_order(post)
            PostMedia.objects.bulk_create(
                [
                    PostMedia(
                        post=post,
                        file=image,
                        type=PostMedia.MediaType.IMAGE,
                        order=index,
                        profile=post.user.profile,
                    )
                    for index, image in enumerate(images, start=max_order + 1)
                ]
            )
        if video:
            PostMedia.objects.create(
                post=post,
                profile=post.user.profile,
                file=video,
                type=PostMedia.MediaType.VIDEO,
                order=-1,
            )

    def _get_max_order(self, post):
        return post.medias.aggregate(max_order=Max("order"))["max_order"] or 0

    def clean(self):
        """Validate allowed media amount."""
        cleaned_data = super().clean()
        self._validate_allowed_media_num(
            objs=cleaned_data.get("images"),
            media_type=PostMedia.MediaType.IMAGE,
            limit_num=ALLOWED_POST_IMAGE_NUM,
        )
        self._validate_allowed_media_num(
            objs=[cleaned_data.get("video")],
            media_type=PostMedia.MediaType.VIDEO,
            limit_num=ALLOWED_POST_VIDEO_NUM,
        )
        return cleaned_data

    def _validate_allowed_media_num(self, objs, media_type, limit_num):
        post = self.instance
        if post.pk:  # when editing
            existing_count = PostMedia.objects.filter(
                type=media_type, post=self.instance
            ).count()
        else:
            existing_count = 0

        new_upload_count = len(objs or [])
        total = existing_count + new_upload_count

        if total > limit_num:
            msg = f"You can only upload up to {limit_num} {media_type}"
            raise forms.ValidationError(msg)

    # TODO (extra) implement validate media size
