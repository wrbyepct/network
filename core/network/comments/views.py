"""Comment Views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.views.generic import CreateView, ListView, UpdateView, View

from network.posts.models import Post

from .forms import CommentForm
from .mixins import (
    CommentCountUpdatedMixin,
    CommentObjectOwnedMixin,
    FormInvalidReturnErrorHXTriggerMixin,
)
from .models import Comment, CommentLike


class SetAssociatedPostContextMixin:
    """Mixin for setting associated post instance."""

    def set_post(self):
        """Set post instance in property. associated with the comment."""
        post_id = self.kwargs.get("post_id")
        if post_id:
            self.post = get_object_or_404(Post, id=self.kwargs.get("post_id"))
        else:
            self.post = self.object.post

    def get_context_data(self, **kwargs):
        """Insert post instance in context."""
        context = super().get_context_data(**kwargs)
        context["post"] = self.post
        return context


class CommentPaginatedView(SetAssociatedPostContextMixin, ListView):
    """Comment Paginated list View."""

    context_object_name = "comments"
    template_name = "comments/paginator.html"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """Save post for later use."""
        self.set_post()
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Get top level comments."""
        return Comment.objects.top_level_comments(
            post=self._post,
            user=self.request.user,
        )


class CommentCreateView(
    LoginRequiredMixin,
    SetAssociatedPostContextMixin,
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

        context = self.get_context_data()

        self.object.liked_by_user = False  # new comment won't be liked by any user.
        context.update(
            {
                "comment": self.object,
                "is_new_comment": True,
                "is_reply": is_reply,
            }
        )
        return render(self.request, template, context)

    def form_valid(self, form):
        """
        Attach post, user, and optional parent to the comment.

        And provide partial comment html.
        """
        self.set_post()

        form.instance.post = self.post
        form.instance.user = self.request.user

        parent_id = self.request.POST.get("parent_id")

        if parent_id:
            form.instance.parent = get_object_or_404(Comment, id=parent_id)

        with transaction.atomic():
            self.object = form.save()
            self.object.post.sync_comment_count()

        return self.get_response()


class CommentUpdateView(
    LoginRequiredMixin,
    SetAssociatedPostContextMixin,
    FormInvalidReturnErrorHXTriggerMixin,
    CommentObjectOwnedMixin,
    UpdateView,
):
    """Comment update view."""

    form_class = CommentForm

    def form_valid(self, form):
        """Return partial comment as response."""
        form.save()

        self.object.set_liked_by_user(user=self.request.user)
        self.set_post()

        context = self.get_context_data()
        context.update({"comment": self.object})

        return render(self.request, "comments/comment.html", context)


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
class CommentChildrenPaginatedView(SetAssociatedPostContextMixin, ListView):
    """Comment Children Partial response view."""

    context_object_name = "replies"
    template_name = "comments/replies.html"
    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):
        """Override to set parent comemnt instance in dispatch."""
        self.object = get_object_or_404(
            Comment, id=self.kwargs.get("parent_id")
        )  # parent comment
        self.set_post()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """Provide request in context for partial template."""
        context = super().get_context_data(**kwargs)
        context["comment"] = self.object  # parent comment
        return context

    def get_queryset(self):
        """Return comment's children as queryset."""
        return Comment.objects.get_children(
            parent=self.object,
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
