"""Comment Views."""

from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.views.generic import CreateView, DeleteView, ListView, UpdateView, View

from network.posts.models import Post

from .forms import CommentForm
from .mixins import CommentObjectOwnedMixin, CommentRenderMixin, CommentSetPostMixin
from .models import Comment, CommentLike

# TODO user see immediate comments update to comment section

# TODO later change comment create view to partial html


class CommentPaginatedView(CommentSetPostMixin, ListView):
    """Comment Paginated list View."""

    context_object_name = "comments"
    template_name = "comments/paginator.html"
    paginate_by = 10

    def get_post(self):
        """Overrise get post."""
        return get_object_or_404(Post, id=self.kwargs.get("post_id"))

    def get_context_data(self, **kwargs):
        """Provide request in context for partial template."""
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        return context

    def get_queryset(self):
        """Get top level comments."""
        return Comment.objects.filter(post=self._post, parent__isnull=True)


class CommentCreateView(CreateView):
    """Comment Create view."""

    context_object_name = "comment"
    form_class = CommentForm

    def form_valid(self, form):
        """Attach post, user, and optional parent to the comment."""
        form.instance.post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        form.instance.user = self.request.user

        parent_id = self.request.POST.get("comment_id")
        if parent_id:
            form.instance.parent = get_object_or_404(Comment, id=parent_id)

        self.object = form.save()

        context = {
            "request": self.request,
            "comment": self.object,
            "padding": 0,
        }
        html = render_to_string("comments/comment.html", context)
        resp = HttpResponse(html)
        resp["HX-Trigger"] = "comment-created"
        return resp


class CommentUpdateView(
    CommentSetPostMixin,
    CommentObjectOwnedMixin,
    CommentRenderMixin,
    UpdateView,
):
    """Comment update view."""

    form_class = CommentForm

    def get_post(self):
        """Overrise get post."""
        return self.comment.post


class CommentDeleteView(
    CommentObjectOwnedMixin,
    CommentSetPostMixin,
    CommentRenderMixin,
    DeleteView,
):
    """Delete a comment owned by user."""

    def get_post(self):
        """Override get post."""
        return self.comment.post


# TODO: make sure this query is optimized
class CommentChildrenPaginatedView(CommentSetPostMixin, ListView):
    """Comment Children Partial response view."""

    context_object_name = "replies"
    template_name = "comments/replies.html"
    paginate_by = 5

    def get_post(self):
        """Override get post."""
        return self.comment.post

    def dispatch(self, request, *args, **kwargs):
        """Override to set comemnt instance in dispatch."""
        self.comment = get_object_or_404(Comment, id=self.kwargs.get("comment_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Provide request in context for partial template."""
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        context["comment"] = self.comment
        return context

    def get_queryset(self):
        """Return comment's children as queryset."""
        return Comment.objects.filter(parent=self.comment)


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
