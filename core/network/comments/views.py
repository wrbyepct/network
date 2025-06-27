"""Comment Views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, UpdateView

from network.posts.models import Post

from .forms import CommentForm
from .models import Comment

# TODO create comment on post
# TODO user see immediate comments update to comment section


# TODO later change comment create view to partial html


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Comment Create view."""

    template_name = "posts/detail.html"  # will be used on form_invalid
    form_class = CommentForm

    def dispatch(self, request, *args, **kwargs):
        """Save post object for later use."""
        self._post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Add post in context data."""
        context = super().get_context_data(**kwargs)
        context["post"] = self._post
        return context

    def get_success_url(self):
        """Return to the post detail page."""
        return reverse_lazy("post_detail", args=[self._post.id])

    def form_valid(self, form):
        """Handle saving user, post and parent comment into instance."""
        form = self.handle_reply_to_post(form)

        parent_id = self.request.POST.get("comment_id")
        if parent_id:
            self.handle_reply_to_comment(form)

        return super().form_valid(form)

    def handle_reply_to_post(self, form):
        """Handle replying to a post."""
        form.instance.user = self.request.user
        form.instance.post = self._post
        return form

    def handle_reply_to_comment(self, form):
        """Handle replying to a comment."""
        form.instance.parent = get_object_or_404(
            Comment, id=self.kwargs.get("comment_id")
        )
        return form


# TODO display user orignal comment content while editing
# TODO prevent user from submitting empty
class CommentUpdateView(UpdateView):
    """Comment update view."""

    template_name = "posts/detail.html"
    form_class = CommentForm

    def get_object(self, queryset=None):
        """Get comment owned by the user."""
        comment = get_object_or_404(
            Comment,
            id=self.kwargs.get("comment_id"),
            user=self.request.user,
        )
        self._post = comment.post
        return comment

    def get_success_url(self):
        """Return to the post detail page."""
        return reverse_lazy("post_detail", args=[self._post.id])

    def get_context_data(self, **kwargs):
        """Add post in context data."""
        context = super().get_context_data(**kwargs)
        context["post"] = self._post
        return context
