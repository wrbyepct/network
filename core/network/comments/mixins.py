"""Comment Mixins."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse

from .models import Comment


class CommentRenderMixin:
    """
    Mixin to render succuss url and template to render on failed.

    Properties:
        - template_name: "posts/detail.html"

    Methods:
        - get_success_url(): Return post page the comment is on.

    """

    template_name = "posts/detail.html"  # will be used on form_invalid

    def get_success_url(self):
        """Return to the post detail page."""
        return reverse("post_detail", args=[self._post.id])


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
