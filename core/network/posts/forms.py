"""Post forms."""

from django import forms

from network.common.constants import ALLOWED_POST_IMAGE_NUM, ALLOWED_POST_VIDEO_NUM
from network.common.fields import MultipleFileField
from network.common.models import MediaBaseModel
from network.common.validators import validate_image_extension, validate_video_extension

from .models import Post, PostMedia


class PostForm(forms.ModelForm):
    """Form for create/edit form."""

    images = MultipleFileField(required=False)
    video = forms.FileField(required=False)
    image_exts = forms.CharField(required=False, validators=[validate_image_extension])
    video_exts = forms.CharField(required=False, validators=[validate_video_extension])
    images_count = forms.IntegerField(required=False)
    videos_count = forms.IntegerField(required=False)

    class Meta:
        model = Post
        fields = ["content", "publish_at"]

    def __init__(self, *args, in_post_create_view=None, **kwargs):  # noqa: ANN204
        super().__init__(*args, **kwargs)
        self.in_post_create_view = in_post_create_view

    def clean(self):
        """Also validate allowed media in full clean."""
        if self.in_post_create_view:
            self.validate_allowed_media_num()
        return super().clean()

    def validate_allowed_media_num(self):
        """Validate allowed media amount."""
        cleaned_data = super().clean()
        self._validate_allowed_media_num(
            uploaded_num=cleaned_data.get("images_count")
            or len(cleaned_data.get("images")),
            media_type=MediaBaseModel.MediaType.IMAGE,
            limit_num=ALLOWED_POST_IMAGE_NUM,
        )

        videos = cleaned_data.get("video")
        self._validate_allowed_media_num(
            uploaded_num=cleaned_data.get("videos_count")
            or len([videos] if videos else []),
            media_type=MediaBaseModel.MediaType.VIDEO,
            limit_num=ALLOWED_POST_VIDEO_NUM,
        )
        return cleaned_data

    def _validate_allowed_media_num(self, uploaded_num, media_type, limit_num):
        post = self.instance
        if post.pk:  # when editing
            existing_count = PostMedia.objects.filter(
                type=media_type, post=self.instance
            ).count()
        else:
            existing_count = 0

        total = existing_count + uploaded_num

        if total > limit_num:
            msg = (
                f"Oops, you can only upload up to {limit_num} {media_type}s in a post."
            )
            raise forms.ValidationError(msg)

    # TODO (extra) implement validate media size
