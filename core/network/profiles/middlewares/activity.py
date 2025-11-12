"""Custom middleware."""

from network.profiles.services import ActivityManagerService


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
        path = request.path.lower()

        is_active_request = any(active_path in path for active_path in ACTIVE_PATHS)
        ActivityManagerService.update_activity_state(
            user_id=request.user.id,
            is_active_request=is_active_request,
        )
