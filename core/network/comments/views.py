"""Comment Views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, UpdateView

from network.posts.models import Post

from .forms import CommentForm
from .models import Comment

# TODO create comment on post
# TODO user see immediate comments update to comment section


# TODO later change comment create view to partial html


class CommentUrlContextMixin(LoginRequiredMixin):
    """
    Mixin to provide success url and context needed for failed submission.

    Properties:
     - template_name: "posts/detail.html"

    Methods:
     - get_success_url(): Return post page the comment is on.
     - get_context_data(): Store post data in

    """

    template_name = "posts/detail.html"  # will be used on form_invalid

    def get_success_url(self):
        """Return to the post detail page."""
        return reverse("post_detail", args=[self._post.id])

    def get_context_data(self, **kwargs):
        """Add post in context data."""
        context = super().get_context_data(**kwargs)
        context["post"] = self._post
        return context


class CommentObjectBaseMixin:
    """
    Base mixin for Views that access specific comment object.

    Methods:
     - dispatch(): set self.comment and self._post
     - get_object(): Get comment owned by the user


    """

    def dispatch(self, request, *args, **kwargs):
        """Set self.comment and self._post."""
        self.comment = get_object_or_404(
            Comment,
            id=self.kwargs.get("comment_id"),
            user=self.request.user,
        )
        self._post = self.comment.post
        return super().dispatch(request, *args, **kwargs)

    def get_object(self):
        """Get comment owned by the user."""
        return self.comment


class CommentCreateView(CommentUrlContextMixin, CreateView):
    """Comment Create view."""

    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        """Save post object for later use."""
        self._post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Attach post, user, and optional parent to the comment."""
        form.instance.post = self._post
        form.instance.user = self.request.user

        parent_id = self.request.POST.get("comment_id")
        if parent_id:
            form.instance.parent = get_object_or_404(Comment, id=parent_id)

        return super().form_valid(form)


# TODO display user orignal comment content while editing
class CommentUpdateView(CommentUrlContextMixin, CommentObjectBaseMixin, UpdateView):
    """Comment update view."""

    form_class = CommentForm


class CommentDeleteView(CommentUrlContextMixin, CommentObjectBaseMixin, DeleteView):
    """Delete a comment owned by user."""
