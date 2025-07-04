"""Comment Mixins."""

import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404

from .models import Comment


class CommentSetPostMixin(LoginRequiredMixin):
    """
    Mixin to provide success url and context needed for failed submission.

    Methods:
     - dispatch: set self._post with custom self.get_post() method.

     - get_context_data(): Store post data in context.

    """

    def dispatch(self, request, *args, **kwargs):
        """Save post for later use."""
        self._post = self.get_post()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add post in context data."""
        context = super().get_context_data(**kwargs)
        context["post"] = self._post
        return context


class CommentObjectOwnedMixin:
    """
    Base mixin for Views that access specific comment object.

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
