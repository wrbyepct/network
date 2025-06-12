"""Post views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import PostForm
from .models import Post, PostMedia

# Create your views here.


# TODO allow user to click avatar picture and get directed to their profile page
# TODO allow like/unlike the post
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


# TODO add permissions later
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

    success_url = reverse_lazy("post_list")

    def get_object(self, queryset=None):
        """Return the requesting post object."""
        post_id = self.kwargs.get("post_id")
        return get_object_or_404(Post, id=post_id, user=self.request.user)
