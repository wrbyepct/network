"""Post Service."""

import json
import random
from datetime import timedelta

from django.utils import timezone

from .constants import EGG_TYPES, MAX_INCUBATION_MINUTES, MIN_INCUBATION_MINUTES


def get_like_stat(like_count, liked) -> str:
    """Return dynamic like stat string to display at the frontend."""
    if like_count == 0:
        return ""

    if liked:
        if like_count == 1:
            return "You"
        return f"You and {like_count - 1} others"

    return str(like_count)


def get_random_publish_time():
    """Return random publish time."""
    random_minutes = random.randint(MIN_INCUBATION_MINUTES, MAX_INCUBATION_MINUTES)
    return timezone.now() + timedelta(seconds=random_minutes)


def get_random_egg_img_index():
    """Return random egg img url."""
    return random.randint(0, 8)


def get_random_egg_type():
    """Return random egg img url."""
    return random.choice(EGG_TYPES)


def get_egg_img_url():
    """Return a random egg url."""
    egg_num = get_random_egg_img_index()
    egg_type = get_random_egg_type()
    return f"media/defaults/{egg_type}/egg{egg_num}.gif"


def set_post_create_event():
    """Return post created event with random egg image url."""
    return json.dumps({"post-created": {"eggUrl": get_egg_img_url()}})
