"""Activity Reader."""

from django.core.cache import cache
from django.utils.timezone import now

"""
Logged in:
    - Swimming: Hit active request 3 times within a time window.
    - Exploring: Any non-active request
    - Resting: No requests for x window

Logged out
    - Sunbathing: Logged out but (last logout < x time).
    - Hiding: No login in x time .
"""


class ActivityStatus:
    """Activity status choices."""

    SWIMMING = "swimming"
    RESTING = "resting"
    EXPLORING = "exploring"
    SUNBATHING = "sunbathing"
    HIDING = "hiding_in_shell"


ACTIVE_THRESHOLD = 3

INACTIVE_THRESHOLD = 30  # seconds


def evaluate_logout_status(user):
    """Evaluate logout status."""
    if (now() - user.last_logout).seconds < INACTIVE_THRESHOLD:
        return ActivityStatus.SUNBATHING
    return ActivityStatus.HIDING


def evaluate_activity_status(user):
    """Determine current activity status based on cached state."""
    active_count = fetch_active_count(user.id)
    last_request = fetch_last_request(user.id)

    if user.is_logged_out:
        return evaluate_logout_status(user)

    if last_request:
        if active_count >= ACTIVE_THRESHOLD:
            return ActivityStatus.SWIMMING
        return ActivityStatus.EXPLORING

    return ActivityStatus.RESTING


def fetch_active_count(user_id):
    """Fetch cached active request count."""
    return int(cache.get(cache_key(user_id, "active_count")) or 0)


def fetch_last_request(user_id):
    """Fetch cahed last request time."""
    return cache.get(cache_key(user_id, "last_request"))


def cache_key(user_id, suffix):
    """Cache key using user id and specified string."""
    return f"user:{user_id}:{suffix}"
