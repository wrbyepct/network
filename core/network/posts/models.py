"""Post models."""

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from network.common.models import TimestampedModel
from network.tools.media import post_media_path

from .managers import PostManger


# Create your models here.
class Post(TimestampedModel):
    """Post model."""

    content = models.TextField(max_length=1280)
    like_count = models.PositiveIntegerField(default=0)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )

    objects = PostManger()

    class Meta(TimestampedModel.Meta):
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        """Return string <user-profile-username>'s post: <post-title>."""
        return f"Post by: {self.user.profile.username}"


class PostLike(TimestampedModel):
    """Like model."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"], name="unique_like_for_post_per_user"
            )
        ]
        indexes = [
            models.Index(fields=["post", "user"]),
        ]


class PostMedia(TimestampedModel):
    """Post image model."""

    class MediaType(models.TextChoices):
        IMAGE = "image", "Image"
        VIDEO = "video", "Video"

    file = models.FileField(upload_to=post_media_path, null=True, blank=True)
    order = models.SmallIntegerField(default=0)
    type = models.CharField(max_length=10, choices=MediaType.choices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="medias",
        null=True,
        blank=True,
    )
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="medias")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["post", "order"], name="Unique order per post."
            )
        ]

    def __str__(self) -> str:
        """Return string "Media Type: {self.type}. Order: {self.order}. From post: {self.post.pkid}."""
        return (
            f"Media Type: {self.type}. Order: {self.order}. From post: {self.post.pkid}"
        )

    def is_image(self):
        """Check the media if type is image."""
        return self.type == self.MediaType.IMAGE

    def is_video(self):
        """Check the media if type is video."""
        return self.type == self.MediaType.VIDEO


# Album model
class Album(TimestampedModel):
    """Album model for profile."""

    name = models.CharField(max_length=255)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="albums"
    )
    photos = models.ManyToManyField(PostMedia, related_name="albums")

    class Meta(TimestampedModel.Meta):
        pass

    @cached_property
    def photo_count(self):
        """Return photo count."""
        return self.photos.all().count()
