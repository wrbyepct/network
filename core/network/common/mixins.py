"""Custom common mixins for views."""

from django.db.models import Max, Model, PositiveSmallIntegerField
from django.forms import ValidationError
from django.utils.functional import cached_property

from network.common.models import MediaBaseModel


class RefererRedirectMixin:
    """Redirect use referer first or fallback to default url."""

    def get_success_url(self):
        """Redirect to referring page after deletion."""
        referer = self.request.META.get("HTTP_REFERER")
        return referer or self.fallback_url


class MediaMixin:
    """
    Form helper methods for handling medias submission.

    Methods:
        - get_max_order(obj: Model): Get max order int from existing medias in the model instance.
        - get_media_type(media: File): Get media type from submitted file.

    """

    def get_max_order(self, obj):
        """Get max order int from existing medias in the model instance."""
        return obj.medias.aggregate(max_order=Max("order"))["max_order"] or 0

    def get_media_type(self, media):
        """Get media type from submitted file."""
        content_type = media.content_type

        if content_type.startswith("image/"):
            return MediaBaseModel.MediaType.IMAGE

        if content_type.startswith("video/"):
            return MediaBaseModel.MediaType.VIDEO
        return ValidationError(f"{media.name} Unknown file content type.")


class SetOwnerProfileMixin:
    """Mixin for setting profile instance for later access."""

    def dispatch(self, request, *args, **kwargs):
        """Set profile instance for later access."""
        self._profile = self.request.user.profile
        return super().dispatch(request, *args, **kwargs)


class ProfileInfoMixin:
    """
    Mixin for model to provide profile info.

    cached_proterties:
        - profile picture url
        - username

    """

    @cached_property
    def profile_picture_url(self):
        """Return profile picture url."""
        return self.user.profile.profile_picture.url

    @cached_property
    def username(self):
        """Return profile username."""
        return self.user.profile.username


class LikeCountMixin(Model):
    """
    Mixin to track and update like count.

    Fields:
        - like_count: PostiveSmallIntergerField
    Methods:
        - sync_like_count: update like_count with db count.

    """

    like_count = PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True

    def sync_like_count(self):
        """Update like_count in object and save it."""
        self.like_count = self.likes.count()
        self.save(update_fields=["like_count"])


class CommentCountMixin(Model):
    """
    Mixin to track and update comment count.

    Fields:
        - comment_count: PostiveSmallIntergerField
    Methods:
        - sync_like_count: update like_count with db count.

    """

    comment_count = PositiveSmallIntegerField(default=0)

    class Meta:
        abstract = True

    def sync_comment_count(self):
        """Update like_count in object and save it."""
        self.comment_count = self.comments.count()
        self.save(update_fields=["comment_count"])
