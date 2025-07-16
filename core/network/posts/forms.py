"""Post forms."""

from django import forms

from network.common.constants import ALLOWED_POST_IMAGE_NUM, ALLOWED_POST_VIDEO_NUM
from network.common.fields import MultipleFileField
from network.common.models import MediaBaseModel
from network.common.validators import validate_image_extension, validate_video_extension

from .models import Post, PostMedia
from .services import PostMediaService


class PostForm(forms.ModelForm):
    """Form for create/edit form."""

    content = forms.CharField(
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": "4",
                "placeholder": "What's on your mind?",
            }
        ),
    )
    images = MultipleFileField(required=False, validators=[validate_image_extension])
    video = MultipleFileField(required=False, validators=[validate_video_extension])

    class Meta:
        model = Post
        fields = ["content"]

    def save_media(self, post):
        """Save cleaned medias."""
        images = self.cleaned_data.get("images")
        video = self.cleaned_data.get("video")
        PostMediaService.save_media(post, images, video)

    def clean(self):
        """Validate allowed media amount."""
        cleaned_data = super().clean()
        self._validate_allowed_media_num(
            objs=cleaned_data.get("images"),
            media_type=MediaBaseModel.MediaType.IMAGE,
            limit_num=ALLOWED_POST_IMAGE_NUM,
        )
        self._validate_allowed_media_num(
            objs=cleaned_data.get("video"),
            media_type=MediaBaseModel.MediaType.VIDEO,
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
            msg = f"You can only upload up to {limit_num} {media_type} at a time."
            raise forms.ValidationError(msg)

    # TODO (extra) implement validate media size
