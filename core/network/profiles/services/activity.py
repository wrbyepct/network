"""Custom profile services."""

import logging

from django.core.cache import cache
from django.utils.timezone import now

logger = logging.getLogger(__name__)
client = cache.client.get_client()


class ActivityStatus:
    """Activity status choices."""

    SWIMMING = "swimming"
    RESTING = "resting"
    EXPLORING = "exploring"
    SUNBATHING = "sunbathing"
    HIDING = "hiding_in_shell"

    CHOICES = [
        (SWIMMING, "Swimming"),
        (RESTING, "Resting"),
        (EXPLORING, "Exploring"),
        (SUNBATHING, "Sunbathing"),
        (HIDING, "Hiding in Shell"),
    ]


ACTIVE_THRESHOLD = 3
WINDOW_SECONDS = 30  # 5 minutes


"""
Logged in:
    - Swimming: Hit active request 5 times within a time window.
    - Exploring: Any non-active request
    - Resting: No requests for 10 mins

Logged out
    - Sunbathing: Logged out but (last seen < X hours ago).
    - Hiding: No login in 7 days.
"""


def cache_key(user_id, suffix):
    """Return a cache key using user id and a specific suffix. e.g. last passive time."""
    return f"user:{user_id}:{suffix}"


def increment_active_count(user_id):
    """Increment active request count and reset the timer."""
    key = cache_key(user_id, "active_count")

    real_key = cache.make_key(key)

    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1)

    client.expire(real_key, WINDOW_SECONDS)


def update_timestamp(user_id, key_suffix):
    """Update activity timestamp."""
    cache.set(
        cache_key(user_id, key_suffix),
        now().isoformat(),
        timeout=WINDOW_SECONDS,
    )


def get_timestamp(user_id, key_suffix):
    """Get activity timestamp."""
    return cache.get(cache_key(user_id, key_suffix))


def get_activity_status(user_id):
    """Get activity status."""
    last_request = get_timestamp(user_id, "last_request")
    key = cache_key(user_id, "active_count")
    active_count = int(cache.get(key) or 0)

    if last_request:
        if active_count >= ACTIVE_THRESHOLD:
            return ActivityStatus.SWIMMING
        return ActivityStatus.EXPLORING

    return ActivityStatus.RESTING


ACTIVITY_OBJECT = {
    "swimming": {"emoji": "🏊‍♂️", "color": "text-blue-500", "status": "Swimming"},
    "resting": {"emoji": "😴", "color": "text-gray-500", "status": "Resting"},
    "exploring": {"emoji": "🧭", "color": "text-green-500", "status": "Exploring"},
    "sunbathing": {"emoji": "🌞", "color": "text-yellow-500", "status": "Sunbathing"},
    "hiding_in_shell": {
        "emoji": "🐢",
        "color": "text-slate-600",
        "status": "Hiding in shell",
    },
}


def get_activity_obj(user_id):
    """Return activity object."""
    status = get_activity_status(user_id)
    if status in ACTIVITY_OBJECT:
        return ACTIVITY_OBJECT[status]
    return None
