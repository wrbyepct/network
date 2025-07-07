# Create your views here.
"""Profile views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import (
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from network.posts.models import Post

from .constants import PHOTO_TABS, PROFILE_TABS
from .forms import ProfileForm
from .models import Profile

# Photo uploads view
# TODO click on the photo will take user to the post it's asscoiated


class ProfileTabsBaseMixin:
    """Profile base view."""

    tabs = PROFILE_TABS

    def dispatch(self, request, *args, **kwargs):
        """Save requesting profile obj and HX-Request for later use."""
        self.is_partial_request = bool(request.headers.get("HX-Request", False))
        self.profile = get_object_or_404(Profile, username=kwargs.get("username"))
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

        return context


class PhotoTabsBaseMixin:
    """Mixin to provide context needed for photo tab view."""

    current_tab = "photos"
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
    TemplateView,
):
    """Photo uploads tab view."""

    current_photo_tab = "uploads"


class PhotosAlbumsView(
    PhotoTabsBaseMixin,
    ProfileTabsBaseMixin,
    TemplateView,
):
    """Photos albums tab view."""

    current_photo_tab = "albums"


class PostsView(ProfileTabsBaseMixin, ListView):
    """Profile Posts view that handles partial and full request."""

    current_tab = "posts"
    context_object_name = "posts"
    paginate_by = 10

    def get_queryset(self):
        """Get prefetched post queryset."""
        return Post.objects.for_list_data().by_user(user=self.profile.user)


class AboutView(ProfileTabsBaseMixin, TemplateView):
    """Profile about view that handles partial and full request."""

    current_tab = "about"


class FollowersView(ProfileTabsBaseMixin, TemplateView):
    """Profile Followers view that handles partial and full request."""

    current_tab = "followers"


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Profile creation view."""

    template_name = "profiles/edit.html"
    form_class = ProfileForm
    success_url = reverse_lazy("profile_edit")

    def get_object(self, queryset=None):
        """Return the requesting user's Profile."""
        return self.request.user.profile


# Following list view
class FollowingView(ListView):
    """Return user's all following profiles."""

    template_name = "profiles/following.html"
    context_object_name = "following"

    def get_queryset(self):
        """Return user's all following profiles."""
        profile = self.request.user.profile
        return profile.following.all()


# Follow/Unfollow
class FollowView(View):
    """View to follow/unfollow a user's profile."""

    def perform_follow(self, profile, to_follow_profile):
        """Peform follow and return message context."""
        profile.follow(to_follow_profile)
        msg = f"You followed {to_follow_profile.username}!"
        return {"follow_message": msg}

    def perform_unfollow(self, profile, to_unfollow_profile):
        """Peform unfollow and return message context."""
        profile.unfollow(to_unfollow_profile)
        msg = f"Unfollowed {to_unfollow_profile.username}."
        return {"follow_message": msg}

    def post(self, request, *args, **kwargs):
        """Follow a profile and return success message."""
        to_profile = get_object_or_404(Profile, username=kwargs.get("username"))
        profile = request.user.profile

        has_followed = profile.has_followed(to_profile)

        if not has_followed:
            context = self.perform_follow(profile, to_profile)

        else:
            context = self.perform_unfollow(profile, to_profile)

        return render(request, "profiles/partials/messages.html", context)
