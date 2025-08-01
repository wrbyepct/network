"""Post models."""

from django.conf import settings
from django.db import models
from django.utils.functional import cached_property

from network.common.mixins import LikeCountMixin, ProfileInfoMixin
from network.common.models import MediaBaseModel, TimestampedModel
from network.profiles.models import Profile

from .managers import PostManager
from .tasks import delete_task
from .validators import validate_publish_time


# Create your models here.
class Post(LikeCountMixin, ProfileInfoMixin, TimestampedModel):
    """Post model."""

    content = models.TextField(max_length=1280)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="posts"
    )
    publish_at = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    # TODO this is ephemeral data, consider implement it other ways like cache or something.
    celery_task_id = models.CharField(max_length=255, blank=True)

    objects = PostManager()

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
        from network.comments.models import Comment

        return Comment.objects.filter(post=self).count()

    @cached_property
    def medias_count(self):
        """Return medias count."""
        return self.medias.count()

    @cached_property
    def ordered_medias(self):
        """Get acending medias of this post."""
        return self.medias.all().order_by("order")

    def delete(self, *args, **kwargs):
        """Override delete method to revoke publish task."""
        if self.celery_task_id:
            delete_task(self.celery_task_id)
        super().delete(*args, **kwargs)

    def clean(self):
        """Validate that publish_at is at least 20 minutes after created_at."""
        if self.publish_at and self.created_at:
            validate_publish_time(self)
        super().clean()


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
        """Return string Media Type: {type}. Order: {order}. From post: {post.pkid}."""
        return (
            f"Media Type: {self.type}. Order: {self.order}. From post: {self.post.pkid}"
        )
