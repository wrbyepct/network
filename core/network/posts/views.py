"""Post views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    UpdateView,
    View,
)

from .forms import PostForm
from .models import Post, PostLike, PostMedia


# TODO (extra) cache the posts result
# TODO (extra) make media load faster
# TODO make about page posts also paginated (scroll loading)
class PostListView(ListView):
    """Post List View."""

    model = Post
    template_name = "posts/list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        """Get optimized post queryset."""
        return Post.objects.for_list_data()


class PostCreateView(LoginRequiredMixin, CreateView):
    """Post Creation View."""

    template_name = "posts/create.html"
    form_class = PostForm
    success_url = reverse_lazy("post_list")

    def form_valid(self, form):
        """Save images and videos to PostMedia if they are valid."""
        with transaction.atomic():
            form.instance.user = self.request.user
            self.object = form.save()
            form.save_media(self.object)

        return super().form_valid(form)


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
            form.save_media(post=self.get_object())
        return super().form_valid(form)


class PostDeleteView(DeleteView):
    """Post Delete View."""

    def get_object(self, queryset=None):
        """Return the requesting post object."""
        post_id = self.kwargs.get("post_id")
        return get_object_or_404(Post, id=post_id, user=self.request.user)

    def get_success_url(self):
        """Redirect to referring page after deletion."""
        referer = self.request.META.get("HTTP_REFERER")
        return referer or reverse_lazy("post_list")


class LikePost(View):
    """Like/Unlike a post view that returns the partial html of likes count."""

    def dispatch(self, request, *args, **kwargs):
        """Redirect to login page instead of sending back partial html."""
        if not request.user.is_authenticated:
            return HttpResponseRedirect(reverse_lazy("account_login"))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Like the post and syncs with post's like_count field."""
        user = self.request.user
        post = get_object_or_404(Post, id=self.kwargs.get("post_id"))

        with transaction.atomic():
            like, created = PostLike.objects.get_or_create(post=post, user=user)
            if not created:
                like.delete()

            post.like_count = post.likes.count()
            post.save()

        html = render_to_string(
            "posts/partial/like_count.html", {"like_count": post.like_count}
        )
        return HttpResponse(html)
