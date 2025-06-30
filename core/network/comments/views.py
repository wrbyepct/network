"""Comment Views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View

from network.posts.models import Post

from .forms import CommentForm
from .models import Comment, CommentLike

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


class CommentPaginatedView(ListView):
    """Comment Paginated list View."""

    context_object_name = "comments"
    template_name = "comments/paginator.html"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """Save post for later use."""
        self.post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Get top level comments."""
        return Comment.objects.filter(post=self.post, parent__isnull=True)

    def get_context_data(self, **kwargs):
        """Provide post in context."""
        context = super().get_context_data(**kwargs)
        context["post"] = self.post
        return context


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


class CommentUpdateView(CommentUrlContextMixin, CommentObjectBaseMixin, UpdateView):
    """Comment update view."""

    form_class = CommentForm


class CommentDeleteView(CommentUrlContextMixin, CommentObjectBaseMixin, DeleteView):
    """Delete a comment owned by user."""


# TODO: make sure this query is optimized
class CommentChildrenView(ListView):
    """Comment Children Partial response view."""

    context_object_name = "replies"
    template_name = "comments/replies.html"

    def get_context_data(self, **kwargs):
        """Provide request in context for partial template."""
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        return context

    def get_queryset(self):
        """Return comment's children as queryset."""
        comment = get_object_or_404(Comment, id=self.kwargs.get("comment_id"))
        return comment.children.all()


class LikeCommentView(View):
    """View to like/unlike a comment."""

    def post(self, request, *args, **kwargs):
        """Like the post and syncs with comment's like_count field."""
        comment = get_object_or_404(Comment, id=kwargs.get("comment_id"))
        user = request.user
        with transaction.atomic():
            like, created = CommentLike.objects.get_or_create(
                user=user, comment=comment
            )
            if not created:
                like.delete()
            comment.update_like_count()
        return render(
            request,
            "posts/partial/like_count.html",
            {"like_count": comment.like_count},
        )
