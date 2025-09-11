"""Post views."""

import json
import random

import redis
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.forms import ValidationError
from django.http import Http404, HttpResponse, StreamingHttpResponse
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
from network.profiles.services import ActivityManagerService

from .forms import PostForm
from .models import Post, PostLike, PostMedia
from .services import EggManageService, IncubationService
from .utils import get_like_stat

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

    def get_context_data(self, **kwargs):
        """Insert incubating post id into context."""
        context = super().get_context_data(**kwargs)
        context["is_incubating"] = bool(
            IncubationService.get_incubating_post_id(self.request.user.id)
        )
        context["profile"] = self.request.user.profile

        if self.request.user.is_authenticated:
            profile = self.request.user.profile
            easter_eggs = profile.easter_eggs
            special_eggs = profile.special_eggs
            regular_eggs = profile.regular_eggs
            context["egg_panels"] = [
                {
                    "label": "EASTER EGGS",
                    "color": "text-pink-300",
                    "shadow": "rgba(255, 255, 0, 0.5)",
                    "count": profile.easter_eggs_count,
                    "egg": random.choice(profile.easter_eggs) if easter_eggs else None,
                },
                {
                    "label": "LEGENDARY",
                    "color": "text-orange-300",
                    "shadow": "rgba(0, 255, 255, 0.5)",
                    "count": profile.special_eggs_count,
                    "egg": random.choice(profile.special_eggs)
                    if special_eggs
                    else None,
                },
                {
                    "label": "CUTE",
                    "color": "text-green-400",
                    "shadow": "rgba(59, 130, 246, 0.5)",
                    "count": profile.regular_eggs_count,
                    "egg": random.choice(profile.regular_eggs)
                    if regular_eggs
                    else None,
                },
            ]

            context["activity"] = ActivityManagerService.get_activity_obj(
                user=self.request.user
            )
        return context


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

    def get_form_kwargs(self):
        """Insert in PostCreateView info for dynamic form validation."""
        kwargs = super().get_form_kwargs()
        kwargs["in_post_create_view"] = True
        return kwargs

    def get_response_template(self, egg_type):
        """Return template based on if the egg is special or not."""
        return (
            "posts/partial/special_egg_modal.html"
            if egg_type != "regular"
            else "posts/partial/egg_modal.html"
        )

    def form_invalid(self, form):
        """Return form errro message through HTMX trigger."""
        error_messages = [
            f"{error}" for field, errors in form.errors.items() for error in errors
        ]

        resp = HttpResponse(status=400)
        resp["HX-Trigger"] = json.dumps(
            {"post-submit-error": {"message": " ".join(error_messages)}}
        )
        return resp

    def form_valid(self, form):
        """Save images and videos to PostMedia if they are valid."""
        user = self.request.user

        with transaction.atomic():
            egg_gif_url = IncubationService.get_random_egg_url()
            egg_static_url = EggManageService.get_static_egg_img_url(egg_gif_url)
            egg = EggManageService.create_egg_or_update_qnt(
                self.request.user, egg_static_url
            )
            form.instance.user = user
            form.instance.egg = egg

            super().form_valid(form)
            form.save_media(self.object)

        IncubationService.incubate_post(self.object, egg_gif_url)
        # Render Resposne
        egg_template = self.get_response_template(egg.egg_type)
        context = {
            "egg_url": egg_gif_url,
            "egg_type": egg.egg_type,
            "egg_name": egg.name,
        }
        resp = render(self.request, egg_template, context)
        resp["HX-Trigger"] = "post-created"
        return resp


class GetUserPostMixin:
    """Mixin to override get_object to retrieve user owned post."""

    def get_object(self, queryset=None):
        """Return the requesting post object."""
        post_id = self.kwargs.get("post_id")
        return get_object_or_404(Post, id=post_id, user=self.request.user)


class PostEditView(LoginRequiredMixin, GetUserPostMixin, UpdateView):
    """Post update view."""

    form_class = PostForm
    success_url = reverse_lazy("index")

    def get_template_names(self):
        """Get tempalte name based from requesting post type."""
        post_type = self.request.POST.get("post_type")

        if post_type == "list_card":
            return ["posts/post/list_card.html"]
        return ["posts/post/detail_card.html"]

    def form_valid(self, form):
        """Handle deleting old files and add new files."""
        delete_ids = json.loads(self.request.POST.get("delete_media", "[]"))
        try:
            with transaction.atomic():
                PostMedia.objects.filter(id__in=delete_ids).delete()
                form.validate_allowed_media_num()  # This must wait for deletion completed first
                super().form_valid(form)
                form.save_media(post=self.object)
        except ValidationError as e:
            # Catch error from validating
            resp = HttpResponse(status=400)
            resp["HX-Trigger"] = json.dumps(
                {"post-submit-error": {"message": " ".join(e.messages)}}
            )
            return resp

        template = self.get_template_names()
        context = {"post": self.object, "insert_to_dom": True}
        return render(self.request, template, context)


class PostDeleteView(RefererRedirectMixin, GetUserPostMixin, DeleteView):
    """Post Delete View."""

    fallback_url = reverse_lazy("index")


class IncubatingEggView(LoginRequiredMixin, View):
    """View to retreive incubating egg tempalte."""

    def get(self, request, **kwargs):
        """Return incubating egg template."""
        user_id = request.GET.get("user_id", request.user.id)
        post_id = IncubationService.get_incubating_post_id(user_id)
        egg_url = IncubationService.get_incubating_egg_url(user_id)
        egg_type = EggManageService.get_egg_type(egg_url)
        if post_id:
            return render(
                request,
                "posts/partial/incubating_egg.html",
                {
                    "post_id": post_id,
                    "egg_url": egg_url,
                    "egg_type": egg_type,
                },
            )
        msg = "The post has hatched. No egg to return."
        raise Http404(msg)


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
