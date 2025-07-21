"""Custom middleware."""

import logging

from network.profiles.services.activity import (
    increment_active_count,
    update_timestamp,
    get_activity_status,
)

logger = logging.getLogger(__name__)


# TODO For demo concept, make it complete later.
ACTIVE_PATHS = [
    "create/",
    "edit/",
    "delete/",
    "follow/",
    "like/",
]


class ActivityStatusMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Optional: Handle pre-processing globally here
        response = self.get_response(request)
        # Optional: Handle post-processing globally here
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):
        if not request.user.is_authenticated:
            return

        user_id = request.user.id
        path = request.path.lower()

        logger.info("Activity Middleware is running")
        logger.info(f"Requesting: {path}")

        if any(active_path in path for active_path in ACTIVE_PATHS):
            increment_active_count(user_id)

            logger.info("Active path requested")

        update_timestamp(user_id, "last_request")
        logger.info(get_activity_status(user_id))
