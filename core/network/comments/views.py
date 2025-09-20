"""Comment Views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
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
        return Comment.objects.top_level_comments(
            post=self._post,
            user=self.request.user,
        )


class CommentCreateView(
    LoginRequiredMixin,
    FormInvalidReturnErrorHXTriggerMixin,
    CommentCountUpdatedMixin,
    CreateView,
):
    """Comment Create view."""

    context_object_name = "comment"
    form_class = CommentForm

    def get_queryset(self):
        """Use prefetched info qs as base queryset."""
        return Comment.objects.prefetched_info_qs(user=self.request.user)

    def get_response(self):
        """Get partial response."""
        is_reply = self.request.POST.get("is_reply") == "true"
        template = (
            "comments/comment.html"
            if is_reply
            else "comments/comment_for_multi_swap.html"
        )

        post = self.object.post

        context = {
            "comment": self.object,
            "is_new_comment": True,
            "is_reply": is_reply,
            "post": post,
        }
        return render(self.request, template, context)

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

        with transaction.atomic():
            self.object = form.save()
            self.object.post.sync_comment_count()

        self.object.user_likes = (
            False  # Indicating new comment is not liked by any requesting user.
        )

        return self.get_response()


class CommentUpdateView(
    LoginRequiredMixin,
    FormInvalidReturnErrorHXTriggerMixin,
    CommentObjectOwnedMixin,
    UpdateView,
):
    """Comment update view."""

    form_class = CommentForm

    def get_queryset(self):
        """Use prefetched info qs as base queryset."""
        return Comment.objects.prefetched_info_qs(user=self.request.user)

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

        with transaction.atomic():
            comment.delete()
            post.sync_comment_count()

        context = {"post": post}

        return render(
            self.request,
            "posts/partial/comment_count.html",
            context,
            status=200,
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
        return Comment.objects.get_children(
            parent=self.parent_comment,
            user=self.request.user,
        )


class LikeCommentView(LoginRequiredMixin, View):
    """View to like/unlike a comment."""

    template_name = "comments/like_count.html"

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
            comment.sync_like_count()

        context = {"comment": comment}

        return render(self.request, self.template_name, context)
