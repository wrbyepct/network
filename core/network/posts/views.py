"""Post views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView

from .forms import PostForm
from .models import Post

# Create your views here.


class PostListView(ListView):
    """Post List View."""

    model = Post
    template_name = "posts/list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        """Get optimized post queryset."""
        return Post.objects.select_related("user__profile").prefetch_related("medias")


class PostCreateView(LoginRequiredMixin, CreateView):
    """Post Creations View."""

    template_name = "posts/create.html"
    form_class = PostForm
    success_url = reverse_lazy("posts_list")

    def form_valid(self, form):
        """Save images and videos to PostMedia if they are valid."""
        # TODO
