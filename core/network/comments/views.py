"""Comment Views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.views.generic import CreateView, ListView, UpdateView, View

from network.posts.models import Post

from .forms import CommentForm
from .mixins import (
    CommentCountUpdatedMixin,
    CommentObjectOwnedMixin,
    FormInvalidReturnErrorHXTriggerMixin,
)
from .models import Comment, CommentLike

# TODO user see immediate comments update to comment section

# TODO later change comment create view to partial html


class CommentPaginatedView(ListView):
    """Comment Paginated list View."""

    context_object_name = "comments"
    template_name = "comments/paginator.html"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """Save post for later use."""
        self._post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Provide request in context for partial template."""
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        context["post"] = self._post
        return context

    def get_queryset(self):
        """Get top level comments."""
        return Comment.objects.top_level_for(self._post)


class CommentCreateView(
    LoginRequiredMixin,
    FormInvalidReturnErrorHXTriggerMixin,
    CommentCountUpdatedMixin,
    CreateView,
):
    """Comment Create view."""

    context_object_name = "comment"
    form_class = CommentForm

    def get_response(self):
        """Get partial response."""
        context = {
            "request": self.request,
            "comment": self.object,
            "is_new_comment": True,
        }
        html = render_to_string("comments/comment.html", context)

        resp = HttpResponse(html)

        post = self.object.post
        return self.attach_new_comment_count(
            resp=resp, comment_count=post.comment_count
        )

    def form_valid(self, form):
        """
        Attach post, user, and optional parent to the comment.

        And provide partial comment html.
        """
        form.instance.post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        form.instance.user = self.request.user

        parent_id = self.request.POST.get("parent_id")

        if parent_id:
            form.instance.parent = get_object_or_404(Comment, id=parent_id)

        self.object = form.save()

        return self.get_response()


class CommentUpdateView(
    LoginRequiredMixin,
    FormInvalidReturnErrorHXTriggerMixin,
    CommentObjectOwnedMixin,
    UpdateView,
):
    """Comment update view."""

    form_class = CommentForm

    def form_valid(self, form):
        """Return partial comment as response."""
        form.save()
        context = {"comment": self.object, "request": self.request}
        html = render_to_string("comments/comment.html", context)
        return HttpResponse(html)


class CommentDeleteView(
    CommentObjectOwnedMixin,
    CommentCountUpdatedMixin,
    View,
):
    """Delete a comment owned by user."""

    def delete(self, request, comment_id, **kwargs):
        """Do the default and override response."""
        comment = get_object_or_404(Comment, id=comment_id, user=request.user)
        post = comment.post

        comment.delete()

        resp = HttpResponse()
        return self.attach_new_comment_count(
            resp=resp, comment_count=post.comment_count
        )


# TODO: make sure this query is optimized
class CommentChildrenPaginatedView(ListView):
    """Comment Children Partial response view."""

    context_object_name = "replies"
    template_name = "comments/replies.html"
    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):
        """Override to set parent comemnt instance in dispatch."""
        self.parent_comment = get_object_or_404(
            Comment, id=self.kwargs.get("parent_id")
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Provide request in context for partial template."""
        context = super().get_context_data(**kwargs)
        context["request"] = self.request
        context["comment"] = self.parent_comment
        return context

    def get_queryset(self):
        """Return comment's children as queryset."""
        return Comment.objects.get_children(parent=self.parent_comment)


class LikeCommentView(LoginRequiredMixin, View):
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
        resp = HttpResponse(str(comment.like_count), content_type="text/plain")
        resp["HX-Trigger"] = "comment-like-update"
        return resp
