"""Album models."""

from django.db import models

from network.common.models import MediaBaseModel, TimestampedModel
from network.profiles.models import Profile


# Album model
class Album(TimestampedModel):
    """Album model for profile."""

    name = models.CharField(max_length=255)
    profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name="albums"
    )


class AlbumMedia(MediaBaseModel):
    """Media model for album."""

    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="medias")

    class Meta(MediaBaseModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["album", "order"], name="Unique order per album."
            )
        ]

    def __str__(self) -> str:
        """Return string "Media Type: {self.type}. Order: {self.order}. From post: {self.post.pkid}."""
        return f"Media Type: {self.type}. Order: {self.order}. From album: {self.album.name}"
