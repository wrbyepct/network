"""Post models."""

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from network.common.mixins import LikeCountMixin, ProfileInfoMixin
from network.common.models import MediaBaseModel, TimestampedModel
from network.profiles.models import Profile

from .managers import PostManger


# Create your models here.
class Post(LikeCountMixin, ProfileInfoMixin, TimestampedModel):
    """Post model."""

    content = models.TextField(max_length=1280)
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

    @cached_property
    def latest_two_comments(self):
        """Fetch first 2 top level comments."""
        return self.comments.top_level_for(self)[:2]

    @cached_property
    def comment_count(self):
        """Return comment count."""
        return self.comments.all().count()


class PostLike(TimestampedModel):
    """Like model."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="likes")

    class Meta(TimestampedModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"], name="unique_like_for_post_per_user"
            )
        ]
        indexes = [
            models.Index(fields=["post", "user"]),
        ]


class PostMedia(MediaBaseModel):
    """Post image model."""

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="medias")
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="medias",
    )

    class Meta(MediaBaseModel.Meta):
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
