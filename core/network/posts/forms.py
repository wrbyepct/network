"""Post forms."""

from django import forms
from django.db.models import Max

from network.common.fields import MultipleFileField

from .constants import ALLOWED_POST_IMAGE_NUM, ALLOWED_POST_VIDEO_NUM
from .models import Album, AlbumMedia, MediaBaseModel, Post, PostMedia
from .validators import (
    validate_image_extension,
    validate_media_extension,
    validate_video_extension,
)


def get_max_order(obj):
    """Get max order of an object that has medias."""
    return obj.medias.aggregate(max_order=Max("order"))["max_order"] or 0


def get_media_type(media):
    """Get media type."""
    content_type = media.content_type

    if content_type.startswith("/image"):
        return MediaBaseModel.MediaType.IMAGE

    if content_type.startswith("/video"):
        return MediaBaseModel.MediaType.VIDEO
    return forms.ValidationError(f"{media.name} Unknown file content type.")


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
    video = MultipleFileField(required=False, validators=[validate_video_extension])

    class Meta:
        model = Post
        fields = ["content"]

    def save_media(self, post):
        """Save media(images/vidoe) after validation if any."""
        images = self.cleaned_data.get("images")
        video = self.cleaned_data.get("video")
        if images:
            max_order = get_max_order(post)
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

    def clean(self):
        """Validate allowed media amount."""
        cleaned_data = super().clean()
        self._validate_allowed_media_num(
            objs=cleaned_data.get("images"),
            media_type=MediaBaseModel.MediaType.IMAGE,
            limit_num=ALLOWED_POST_IMAGE_NUM,
        )
        self._validate_allowed_media_num(
            objs=[cleaned_data.get("video")],  # clean data of video is not a list.
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
            msg = f"You can only upload up to {limit_num} {media_type}"
            raise forms.ValidationError(msg)

    # TODO (extra) implement validate media size


class AlbumForm(forms.ModelForm):
    """Album form."""

    medias = MultipleFileField(required=False, validators=[validate_media_extension])

    class Meta:
        model = Album
        fields = ["name"]

    def save_medias(self, album):
        """Save valid uploaded media to album."""
        medias = self.cleaned_data.get("medias")
        max_order = get_max_order(album)
        if medias:
            AlbumMedia.objects.bulk_create(
                [
                    AlbumMedia(
                        album=album,
                        file=media,
                        order=index,
                        type=get_media_type(media),
                    )
                    for index, media in enumerate(medias, start=max_order + 1)
                ]
            )
