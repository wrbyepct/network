"""Custom Base model."""

from uuid import uuid4

from django.db import models

from network.tools.media import post_media_path


class TimestampedModel(models.Model):
    """Custom Base timstamped model with uuid and pkid for internal use."""

    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at", "-updated_at"]


class MediaBaseModel(TimestampedModel):
    """
    Media Base model.

    Fields:
        - file(file): file saved is uploaded to what 'post_media_path' specifies
        - order(int):
        - type(char): 'image' or 'video'

    Methods:
        - is_image: check if the instance is from type image
        - is_video : check if the instance is from type video

    """

    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    file = models.FileField(upload_to=post_media_path, null=True, blank=True)
    order = models.SmallIntegerField(default=0)
    type = models.CharField(max_length=10, choices=MediaType.choices)

    class Meta(TimestampedModel.Meta):
        abstract = True

    def is_image(self):
        """Check the media if type is image."""
        return self.type == self.MediaType.IMAGE

    def is_video(self):
        """Check the media if type is video."""
        return self.type == self.MediaType.VIDEO
