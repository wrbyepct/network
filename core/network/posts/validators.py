"""Post validators."""

from datetime import timedelta

from django.core.exceptions import ValidationError

from .constants import MIN_INCUBATION_MINUTES


def validate_publish_time(post):
    """Validate post publish time."""
    min_publish_time = post.created_at + timedelta(minutes=MIN_INCUBATION_MINUTES)
    if post.publish_at < min_publish_time:
        raise ValidationError(
            {"publish_at": "Publish time must be at least 20 minutes after creation."}
        )
