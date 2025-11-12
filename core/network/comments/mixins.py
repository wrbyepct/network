"""Comment Mixins."""

import json

from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Comment


class CommentObjectOwnedMixin:
    """
    Base mixin for Views that access user owned comment object.

    Methods:
     - dispatch(): set self.comment
     - get_object(): Get comment owned by the user

    """

    def dispatch(self, request, *args, **kwargs):
        """Set self.comment."""
        self.comment = get_object_or_404(
            Comment,
            id=self.kwargs.get("comment_id"),
            user=self.request.user,
        )

        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        """Get comment owned by the user."""
        return self.comment


class FormInvalidReturnErrorHXTriggerMixin:
    """Mixin to return error hx trigger when form is invalid."""

    def form_invalid(self, form):
        """Return 400 response with error HX-trigger for alert message."""
        resp = HttpResponse(status=400)

        # Messag for alert.
        error_str = "\n".join(
            [
                f"{field}: {error}"
                for field, errors in form.errors.items()
                for error in errors
            ]
        )

        resp["HX-Trigger"] = json.dumps({"form-error": error_str})
        return resp


class CommentCountUpdatedMixin:
    """Mixin to attach new comment count in HX-Trigger event."""

    def attach_new_comment_count(self, resp, comment_count):
        """Attach new comment count in HX-Trigger event."""
        resp["HX-Trigger"] = json.dumps({"comment-count-updated": comment_count})
        return resp
