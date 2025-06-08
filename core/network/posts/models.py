"""Post models."""

from django.conf import settings
from django.db import models

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

    class Meta:
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["user", "-created_at"]),
        ]

    def __str__(self) -> str:
        """Return string <user-profile-username>'s post: <post-title>."""
        return f"{self.user.profile.username}'s post: {self.title}"


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
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="medias")
    type = models.CharField(max_length=10, choices=MediaType.choices)
    order = models.PositiveSmallIntegerField(default=0)

    def is_image(self):
        """Check the media if type is image."""
        return self.type == self.MediaType.IMAGE

    def is_video(self):
        """Check the media if type is video."""
        return self.type == self.MediaType.VIDEO
