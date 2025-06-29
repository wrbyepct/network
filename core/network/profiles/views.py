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

from .forms import ProfileForm
from .mixins import PartialPhotoTabMixin, ProfileContextMixin, ProfileTabMixin
from .models import Profile


class ProfileBaseTabView(ProfileContextMixin, ProfileTabMixin, TemplateView):
    """Profile base view."""

    def get_template_names(self):
        """Dynamically return partial or full tab template based on requests."""
        return [self.get_tab_template_path()]

    def get_context_data(self, **kwargs):
        """Provide user profile and profile tab context."""
        context = super().get_context_data(**kwargs)
        context.update(self.get_profile_context())
        context.update(self.get_tab_context())

        return context


# Base photo view.
class ProfilePhotoBaseView(PartialPhotoTabMixin, ProfileBaseTabView):
    """Base view photo page."""

    profile_tab = "photos"

    def get_context_data(self, **kwargs):
        """Provide photo tabs constant for frontend."""
        context = super().get_context_data(**kwargs)

        if self.photo_partial_key is None:  # Fallbacks to full page request
            # Render data for photo_content block in partial photos.html
            context["photo_content"] = self.get_partial_rendered_string(context)
        return context


# Photo uploads view
# TODO infinite scroll loading for uploads tab
# TODO click on the photo will take user to the post it's asscoiated
class PhotosUploadsView(ProfilePhotoBaseView):
    """Profile photos view that handles partial and full request."""

    active_tab = "uploads"


# Photo albums view
class PhotoAlbumView(ProfilePhotoBaseView):
    """View to handle profile albums page."""

    active_tab = "albums"

    def get_template_names(self):
        """Return full photo page html."""
        return "profiles/tabs/full/photos.html"


class AboutView(ProfileBaseTabView):
    """Profile about view that handles partial and full request."""

    profile_tab = "about"


class FollowersView(ProfileBaseTabView):
    """Profile Followers view that handles partial and full request."""

    profile_tab = "followers"


# TODO infinite scroll loading for posts tab
class PostsView(ProfileBaseTabView):
    """Profile Posts view that handles partial and full request."""

    profile_tab = "posts"

    def get_context_data(self, **kwargs):
        """Retrieve only user's posts."""
        context = super().get_context_data(**kwargs)
        user = self._profile.user
        # self.request.user.posts can't use custom query methods
        # So we have to use Post model directly
        context["posts"] = Post.objects.for_list_data().by_user(user=user)
        return context


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
