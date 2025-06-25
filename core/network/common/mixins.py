"""Custom common mixins for views."""

from django.db.models import Max
from django.forms import ValidationError

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
