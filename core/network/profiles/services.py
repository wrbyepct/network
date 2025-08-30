"""Activity Reader."""

from django.core.cache import cache
from django.utils.timezone import now

"""
Specs:
Logged in:
    - Swimming: Hit active request 3 times within a time window.
    - Exploring: Any non-active request
    - Resting: No requests for x time window

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


def cache_key(user_id, suffix):
    """Cache key using user id and specified string."""
    return f"user:{user_id}:{suffix}"


class ActivityManagerService:
    """
    Activity managing service for retrieve and update user's activity data.

    It uses ActivityReaderSerivce to retrieve user activity cache data,
    and ActivityWriterSerivce to update user activity cache data.

    """

    ACTIVITY_OBJECT = {
        "swimming": {
            "image": "/media/defaults/turtle_proud.png",
            "color": "text-blue-400",
            "status": "Swimming",
        },
        "resting": {
            "image": "/media/defaults/turtle_following.png",
            "color": "text-gray-500",
            "status": "Resting",
        },
        "exploring": {
            "image": "/media/defaults/turtle_walking.gif",
            "color": "text-green-500",
            "status": "Exploring",
        },
        "sunbathing": {
            "image": "/media/defaults/turtle_hurray.png",
            "color": "text-yellow-500",
            "status": "Sunbathing",
        },
        "hiding_in_shell": {
            "image": "/media/defaults/turtle_hiding.png",
            "color": "text-stone-300",
            "status": "Hiding in shell",
        },
    }

    @staticmethod
    def update_activity_state(user_id, is_active_request):
        """Update user activity counters & timestamps based on request type."""
        if is_active_request:
            ActvitiyWriterService.increment_active_count(user_id)
        ActvitiyWriterService.update_last_request_timeout(user_id)

    @staticmethod
    def get_current_activity_status(user):
        """Public read API for views/templates."""
        return ActivityReaderService.evaluate_activity_status(user)

    @staticmethod
    def get_activity_obj(user):
        """Return activity object."""
        status = ActivityReaderService.evaluate_activity_status(user)
        if status in ActivityManagerService.ACTIVITY_OBJECT:
            return ActivityManagerService.ACTIVITY_OBJECT[status]
        return None


class ActivityReaderService:
    """Service to read and return correct user activity status."""

    ACTIVE_THRESHOLD = 3

    ACTIVE_TIMEOUT_SECONDS = 30  # seconds

    @staticmethod
    def evaluate_logout_status(user):
        """Evaluate logout status."""
        if (
            now() - user.last_logout
        ).seconds > ActivityReaderService.ACTIVE_TIMEOUT_SECONDS:
            return ActivityStatus.HIDING
        return ActivityStatus.SUNBATHING

    @staticmethod
    def evaluate_activity_status(user):
        """Determine current activity status based on cached state."""
        active_count = ActivityReaderService.fetch_active_count(user.id)
        last_request = ActivityReaderService.fetch_last_request(user.id)

        if user.is_logged_out:
            return ActivityReaderService.evaluate_logout_status(user)

        if last_request:
            if active_count >= ActivityReaderService.ACTIVE_THRESHOLD:
                return ActivityStatus.SWIMMING
            return ActivityStatus.EXPLORING

        return ActivityStatus.RESTING

    @staticmethod
    def fetch_active_count(user_id):
        """Fetch cached active request count."""
        return int(cache.get(cache_key(user_id, "active_count")) or 0)

    @staticmethod
    def fetch_last_request(user_id):
        """Fetch cahed last request time."""
        return cache.get(cache_key(user_id, "last_request"))


class ActvitiyWriterService:
    """Service to update user activity cached data and timeout."""

    TIMEOUT_SECONDS = 30  # 30 seconds sliding window for active tracking

    @staticmethod
    def increment_active_count(user_id):
        """Increment active request count and reset TTL."""
        key = cache_key(user_id, "active_count")
        try:
            cache.incr(key)
        except ValueError:
            cache.set(key, 1)
        ActvitiyWriterService.expire_key(key)

    @staticmethod
    def expire_key(key):
        """Set expiry for a Redis key."""
        real_key = cache.make_key(key)
        cache.client.get_client().expire(
            real_key,
            ActvitiyWriterService.TIMEOUT_SECONDS,
        )

    @staticmethod
    def update_last_request_timeout(user_id):
        """Update last request timestamp."""
        cache.set(
            cache_key(user_id, "last_request"),
            now().isoformat(),
            timeout=ActvitiyWriterService.TIMEOUT_SECONDS,
        )
