"""Post views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
    View,
)

from network.common.mixins import RefererRedirectMixin

from .forms import PostForm
from .models import Post, PostLike, PostMedia

# TODO (extra) cache the posts result
# TODO (extra) make media load faster


class PostListView(ListView):
    """Post List View."""

    template_name = "posts/list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        """Get optimized post queryset."""
        return Post.objects.for_list_data()


class PostDetailView(DetailView):
    """Detail view for specified post."""

    context_object_name = "post"
    template_name = "posts/detail.html"

    def get_object(self, queryset=None):
        """Get post by id."""
        return get_object_or_404(Post, id=self.kwargs.get("post_id"))


class PostCreateView(LoginRequiredMixin, CreateView):
    """Post Creation View."""

    template_name = "posts/create.html"
    form_class = PostForm
    success_url = reverse_lazy("post_list")

    def form_valid(self, form):
        """Save images and videos to PostMedia if they are valid."""
        with transaction.atomic():
            form.instance.user = self.request.user
            resp = super().form_valid(form)
            form.save_media(self.object)

        return resp


class PostEditView(LoginRequiredMixin, UpdateView):
    """Post update view."""

    template_name = "posts/edit.html"
    form_class = PostForm
    success_url = reverse_lazy("post_list")

    def get_object(self, queryset=None):
        """Return the requesting post object."""
        post_id = self.kwargs.get("post_id")
        return get_object_or_404(Post, id=post_id, user=self.request.user)

    def form_valid(self, form):
        """Handle deleting old files and add new files."""
        delete_ids = self.request.POST.getlist("delete_media")

        with transaction.atomic():
            PostMedia.objects.filter(id__in=delete_ids).delete()
            resp = super().form_valid(form)
            form.save_media(post=self.object)
        return resp


class PostDeleteView(RefererRedirectMixin, DeleteView):
    """Post Delete View."""

    fallback_url = reverse_lazy("post_list")

    def get_object(self, queryset=None):
        """Return the requesting post object."""
        post_id = self.kwargs.get("post_id")
        return get_object_or_404(Post, id=post_id, user=self.request.user)


class LikePost(View):
    """Like/Unlike a post view that returns the partial html of likes count."""

    def post(self, request, *args, **kwargs):
        """Like the post and syncs with post's like_count field."""
        user = self.request.user
        post = get_object_or_404(Post, id=kwargs.get("post_id"))

        with transaction.atomic():
            like, created = PostLike.objects.get_or_create(post=post, user=user)
            if not created:
                like.delete()

            post.update_like_count()

        return render(
            request,
            "posts/partial/like_count.html",
            {"like_count": post.like_count},
        )
