"""Post views."""

import json

import redis
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import StreamingHttpResponse
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
from .services import IncubationService
from .utils import get_like_stat, set_post_create_event

# Initialize Redis client
redis_client = redis.StrictRedis(host="redis", port=6379, db=0)


# TODO (extra) cache the posts result
class PostListView(ListView):
    """Post List View."""

    template_name = "posts/list.html"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        """Get optimized post queryset."""
        return Post.objects.published()


class PostModalView(DetailView):
    """View to provide modal window of a post."""

    context_object_name = "post"
    template_name = "posts/post/modal.html"

    def get_object(self):
        """Get post by id."""
        return get_object_or_404(
            Post.objects.published(), id=self.kwargs.get("post_id")
        )


class PostCreateView(LoginRequiredMixin, CreateView):
    """Post Creation View."""

    template_name = "posts/create.html"
    form_class = PostForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        """Save images and videos to PostMedia if they are valid."""
        user = self.request.user
        with transaction.atomic():
            form.instance.user = user
            # Set a random publish_at time between 20 minutes and 24 hours from now
            super().form_valid(form)
            form.save_media(self.object)

        egg_url = IncubationService.get_random_egg_url()
        IncubationService.incubate_post(self.object, egg_url)
        resp = render(
            self.request,
            "posts/partial/incubating_egg.html",
            {"post_id": self.object.id},
        )
        resp["HX-Trigger"] = set_post_create_event(egg_url)
        return resp


class GetUserPostMixin:
    """Mixin to override get_object to retrieve user owned post."""

    def get_object(self, queryset=None):
        """Return the requesting post object."""
        post_id = self.kwargs.get("post_id")
        return get_object_or_404(Post, id=post_id, user=self.request.user)


class PostEditView(LoginRequiredMixin, GetUserPostMixin, UpdateView):
    """Post update view."""

    template_name = "posts/edit.html"
    form_class = PostForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        """Handle deleting old files and add new files."""
        delete_ids = self.request.POST.getlist("delete_media")

        with transaction.atomic():
            PostMedia.objects.filter(id__in=delete_ids).delete()
            resp = super().form_valid(form)
            form.save_media(post=self.object)
        return resp


class PostDeleteView(RefererRedirectMixin, GetUserPostMixin, DeleteView):
    """Post Delete View."""

    fallback_url = reverse_lazy("index")


class HatchedPostView(LoginRequiredMixin, DetailView):
    """View to retrieve for hatched post list card."""

    context_object_name = "post"
    template_name = "posts/post/list_card.html"

    def get_object(self):
        """Get post by id."""
        return get_object_or_404(
            Post.objects.published(), id=self.kwargs.get("post_id")
        )


class PostHatchCheckView(LoginRequiredMixin, View):
    """SSE endpoint to check if a post has hatched."""

    def get(self, request, *args, **kwargs):
        """Return StreamResponse for frontend to listen to hatching event."""

        def event_stream():
            pubsub = redis_client.pubsub()
            pubsub.subscribe("post_hatch_events")
            for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    yield f"event: hatch\ndata: {json.dumps(data)}\n\n"

        response = StreamingHttpResponse(
            event_stream(), content_type="text/event-stream"
        )
        response["Cache-Control"] = "no-cache"
        return response


class LikePost(LoginRequiredMixin, View):
    """Like/Unlike a post view that returns the partial html of likes count."""

    template_name = "posts/partial/like_stat.html"

    def post(self, request, *args, **kwargs):
        """Like the post and syncs with post's like_count field."""
        user = self.request.user
        post = get_object_or_404(Post, id=kwargs.get("post_id"))

        with transaction.atomic():
            like, created = PostLike.objects.get_or_create(post=post, user=user)
            if created:
                post.add_one_like_count()
            else:
                like.delete()
                post.subtract_one_like_count()

        like_stat = get_like_stat(post.like_count, liked=created)

        context = {
            "like_stat": like_stat,
            "post_id": post.id,
        }

        return render(request, self.template_name, context)
