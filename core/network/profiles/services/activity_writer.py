"""Activity Writer service."""

from django.core.cache import cache
from django.utils.timezone import now

from .activity_reader import cache_key

WINDOW_SECONDS = 30  # 30 seconds sliding window for active tracking


def increment_active_count(user_id):
    """Increment active request count and reset TTL."""
    key = cache_key(user_id, "active_count")
    try:
        cache.incr(key)
    except ValueError:
        cache.set(key, 1)
    expire_key(key)


def expire_key(key):
    """Set expiry for a Redis key."""
    real_key = cache.make_key(key)
    cache.client.get_client().expire(real_key, WINDOW_SECONDS)


def update_last_request(user_id):
    """Update last request timestamp."""
    cache.set(
        cache_key(user_id, "last_request"), now().isoformat(), timeout=WINDOW_SECONDS
    )
