# Create your views here.
"""Profile views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, UpdateView, View

from network.posts.models import Post

from .constants import photo_tabs, profile_tabs
from .forms import ProfileForm
from .models import Profile


class ProfileBaseTabView(TemplateView):
    """Profile base view."""

    def get_template_names(self):
        """Dynamically return partial or full tab template based on requests."""
        is_partial_request = self.request.GET.get("is_partial_request", None) == "true"
        request_page_str = self.request.path.rstrip("/").split("/")[-1]

        sub_path = (
            f"partial/{request_page_str}"
            if is_partial_request
            else f"full/{request_page_str}"
        )

        return f"profiles/tabs/{sub_path}.html"

    def get_context_data(self, **kwargs):
        """Provide user profile and profile tab context."""
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, username=self.kwargs["username"])
        context["profile"] = profile
        context["tabs"] = profile_tabs
        context["current_tab"] = self.profile_tab

        return context


#####################
# Profile Tab views #
#####################


# Base photo view.
class ProfilePhotoBaseView(ProfileBaseTabView):
    """Base view photo page."""

    profile_tab = "photos"

    def get_context_data(self, **kwargs):
        """Provide photo tabs constant for frontend."""
        context = super().get_context_data(**kwargs)
        context["photo_tabs"] = photo_tabs
        context["current_photo_tab"] = self.active_tab

        # Render data for photo_content block in partial photos.html
        context["photo_content"] = render_to_string(self.partial_template, context)
        return context


# Photo uploads view
class ProfilePhotosView(ProfilePhotoBaseView):
    """Profile photos view that handles partial and full request."""

    partial_template = "profiles/tabs/partial/photo_partials/uploads.html"
    active_tab = "uploads"


# Photo albums view
class ProfilePhotoAlbumFullView(ProfilePhotoBaseView):
    """View to handle profile albums page."""

    partial_template = "profiles/tabs/partial/photo_partials/albums.html"
    active_tab = "albums"

    def get_template_names(self):
        """Return full photo page html."""
        return "profiles/tabs/full/photos.html"


# Base photos partial views
class ProfilePhotoParialBaseView(TemplateView):
    """Base view for partial photo content."""

    def get_context_data(self, **kwargs):
        """Provide user profile in context."""
        profile = get_object_or_404(Profile, username=kwargs.get("username"))
        context = super().get_context_data(**kwargs)
        context["profile"] = profile
        return context


# Photos uploads view
class ProfilePhotoUploadsPartialView(ProfilePhotoParialBaseView):
    """Render partail photo uploads view."""

    template_name = "profiles/tabs/partial/photo_partials/uploads.html"


# photos albums view
class ProfilePhotoAlbumsPartialView(ProfilePhotoParialBaseView):
    """Render partail photo albums view."""

    template_name = "profiles/tabs/partial/photo_partials/albums.html"


class ProfileAboutView(ProfileBaseTabView):
    """Profile about view that handles partial and full request."""

    profile_tab = "about"


class ProfileFollowersView(ProfileBaseTabView):
    """Profile Followers view that handles partial and full request."""

    profile_tab = "followers"


class ProfilePostsView(ProfileBaseTabView):
    """Profile Posts view that handles partial and full request."""

    profile_tab = "posts"

    def get_context_data(self, **kwargs):
        """Retrieve only user's posts."""
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, username=self.kwargs["username"])
        user = profile.user
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
    """View to follow a user's profile."""

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
