"""Comment models."""

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models

from network.common.mixins import LikeCountMixin, ProfileInfoMixin
from network.common.models import TimestampedModel
from network.posts.models import Post

from .managers import CommentManager


class Comment(ProfileInfoMixin, LikeCountMixin, TimestampedModel):
    """Commnet model associated with a Post."""

    content = models.TextField(validators=[MinLengthValidator(1)])

    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comments"
    )
    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="children",
    )

    objects = CommentManager()

    class Meta(TimestampedModel.Meta):
        pass

    def __str__(self) -> str:
        """Return string: 'User: {self.user.id} comment on Post: {self.post.id}'."""
        return f"User: {self.user.id} comment on Post: {self.post.id}"

    def set_liked_by_user(self, user):
        """Set update-to-date liked by user for comment."""
        self.liked_by_user = self.likes.filter(user=user).exists()


class CommentLike(TimestampedModel):
    """Like model for comment."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="comment_likes"
    )
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="likes")

    class Meta(TimestampedModel.Meta):
        constraints = [
            models.UniqueConstraint(
                fields=["user", "comment"], name="unique_like_per_comment"
            )
        ]
