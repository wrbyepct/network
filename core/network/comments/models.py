"""Comment models."""

from django.conf import settings
from django.core.validators import MinLengthValidator
from django.db import models

from network.common.models import TimestampedModel
from network.posts.models import Post


class Comment(TimestampedModel):
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

    def __str__(self) -> str:
        """Return string: 'User: {self.user.id} comment on Post: {self.post.id}'."""
        return f"User: {self.user.id} comment on Post: {self.post.id}"
