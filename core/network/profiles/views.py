# Create your views here.
"""Profile views."""

import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from network.posts.models import Post, PostMedia
from network.posts.services import IncubationService

from .constants import PHOTO_TABS, PROFILE_TABS
from .forms import ProfileForm
from .models import Profile


# Photo uploads view
class ProfileTabsBaseMixin:
    """Profile base view."""

    tabs = PROFILE_TABS

    def dispatch(self, request, *args, **kwargs):
        """Save requesting profile obj and HX-Request for later use."""
        # TODO refector this using django htmx later
        self.is_partial_request = bool(request.headers.get("HX-Request", False))
        self.profile = get_object_or_404(
            Profile.objects.select_related("user"),
            username=kwargs.get("username"),
        )
        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        """Provide partial or full template based on partial request or not."""
        _, tab = self.request.path.rstrip("/").rsplit("/", 1)

        if self.is_partial_request:
            return [f"profiles/tabs/partial/{tab}.html"]
        return [f"profiles/tabs/full/{tab}.html"]

    def get_context_data(self, **kwargs):
        """Provide context data based on partial request."""
        context = super().get_context_data(**kwargs)
        if not self.is_partial_request:
            context["tabs"] = self.tabs
            context["current_tab"] = self.current_tab

        context["profile"] = self.profile
        context["is_incubating"] = bool(
            IncubationService.get_incubating_post_id(self.profile.user.id)
        )

        return context


class PhotoTabsBaseMixin:
    """Mixin to provide context needed for photo tab view."""

    current_tab = "shells"
    photo_tabs = PHOTO_TABS

    def get_context_data(self, **kwargs):
        """Provide context data based on partial request."""
        context = super().get_context_data(**kwargs)
        context["photo_tabs"] = self.photo_tabs
        context["current_photo_tab"] = self.current_photo_tab

        return context


class PhotosView(
    PhotoTabsBaseMixin,
    ProfileTabsBaseMixin,
    TemplateView,
):
    """
    Profile Photos view that handles partial and full request.

    Default to fetch photo tab view.
    """

    current_photo_tab = "uploads"


class PhotosUploadsView(
    PhotoTabsBaseMixin,
    ProfileTabsBaseMixin,
    ListView,
):
    """Photo uploads tab view."""

    current_photo_tab = "uploads"
    context_object_name = "medias"
    paginate_by = 10

    def get_queryset(self):
        """Get uploads media owned by the profile."""
        return PostMedia.objects.filter(profile=self.profile)


class PhotosAlbumsView(
    PhotoTabsBaseMixin,
    ProfileTabsBaseMixin,
    TemplateView,
):
    """
    Photos albums tab view.

    Return basic album template, then fetch albums on load via AlbumsPaginateView
    """

    current_photo_tab = "albums"


class PostsView(ProfileTabsBaseMixin, ListView):
    """Profile Posts view that handles partial and full request."""

    current_tab = "turties"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        """Get prefetched post queryset."""
        return Post.objects.for_list_data().by_user(user=self.profile.user)


class NestView(ProfileTabsBaseMixin, TemplateView):
    """Profile nest view that handles partial and full request."""

    current_tab = "nest"

    def get_context_data(self, **kwargs):
        """Inject user eggs into context."""
        context = super().get_context_data(**kwargs)

        eggs = [
            {"name": "special", "eggs": self.profile.special_eggs},
            {"name": "regular", "eggs": self.profile.regular_eggs},
            {"name": "easter", "eggs": self.profile.easter_eggs},
        ]
        context["eggs"] = eggs

        return context


class AboutView(LoginRequiredMixin, ProfileTabsBaseMixin, TemplateView):
    """Profile about view that handles partial and full request."""

    current_tab = "about"

    def get_context_data(self, **kwargs):
        """Inject user activity status in context."""
        context = super().get_context_data(**kwargs)

        context["sub_tab"] = self.request.GET.get("sub_tab", "story")

        return context


class FollowTabView(LoginRequiredMixin, ProfileTabsBaseMixin, TemplateView):
    """Profile Followers view that handles partial and full request."""

    current_tab = "follow"


class FollowPaginatorBaseView(ListView):
    """Follow Paginator Base View."""

    paginate_by = 3

    def get_template_names(self):
        """Get dynamic follow type tempalte name."""
        return [f"profiles/tabs/partial/{self.follow_type}_paginator.html"]

    def get_context_object_name(self, object_list):
        """Get dynamic follow type context object name."""
        return self.follow_type

    def get_queryset(self):
        """Get dynamic follow type related objects from a profile."""
        profile = get_object_or_404(Profile, username=self.kwargs.get("username"))

        return getattr(profile, f"{self.follow_type}").all()

    def get_context_data(self, **kwargs):
        """Inject requesting username to context."""
        context = super().get_context_data(**kwargs)
        context["username"] = self.kwargs.get("username")
        return context


class FollowersPaginatorView(FollowPaginatorBaseView):
    """Following Paginator View."""

    follow_type = "followers"


class FollowingPaginatorView(FollowPaginatorBaseView):
    """Following Paginator View."""

    follow_type = "following"


# Follow/Unfollow
class FollowView(View):
    """View to follow/unfollow a user's profile."""

    def perform_follow(self, profile, to_follow_profile):
        """Peform follow and return message."""
        profile.follow(to_follow_profile)
        return f"You followed {to_follow_profile.username}!"

    def perform_unfollow(self, profile, to_unfollow_profile):
        """Peform unfollow and return message."""
        profile.unfollow(to_unfollow_profile)
        return f"Unfollowed {to_unfollow_profile.username}"

    def post(self, request, *args, **kwargs):
        """Follow a profile and return success message."""
        to_profile = get_object_or_404(Profile, username=kwargs.get("username"))
        profile = request.user.profile

        has_followed = profile.has_followed(to_profile)

        if not has_followed:
            message = self.perform_follow(profile, to_profile)

        else:
            message = self.perform_unfollow(profile, to_profile)

        resp = render(
            self.request, "profiles/tabs/partial/follow.html", {"profile": profile}
        )

        resp["HX-Trigger"] = json.dumps({"follow-success": {"message": message}})
        return resp


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Profile creation view."""

    template_name = "profiles/edit.html"
    form_class = ProfileForm
    success_url = reverse_lazy("profile_edit")

    def get_object(self, queryset=None):
        """Return the requesting user's Profile."""
        return self.request.user.profile

    def form_valid(self, form):
        """Inject exited success to true when the edit is successful."""
        super().form_valid(form)
        context = {"edited_success": True, "form": form}
        return render(self.request, self.template_name, context)
