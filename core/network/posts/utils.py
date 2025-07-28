"""Post Service."""

import json
import random
from datetime import timedelta

from django.utils import timezone

from .constants import MAX_INCUBATION_MINUTES, MIN_INCUBATION_MINUTES


def get_like_stat(like_count, liked) -> str:
    """Return dynamic like stat string to display at the frontend."""
    if like_count == 0:
        return ""

    if liked:
        if like_count == 1:
            return "You"
        return f"You and {like_count - 1} others"

    return str(like_count)


def get_random_timeout():
    """Return random timeout in seconds."""
    return random.randint(MIN_INCUBATION_MINUTES, MAX_INCUBATION_MINUTES)


def get_random_publish_time(timeout):
    """Return random publish time."""
    return timezone.now() + timedelta(seconds=timeout)


def set_post_create_event(egg_url):
    """Return post created event with random egg image url."""
    return json.dumps({"post-created": {"eggUrl": egg_url}})
