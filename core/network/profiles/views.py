# Create your views here.
"""Profile views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.views.generic import ListView, TemplateView, UpdateView, View

from network.posts.models import Post

from .constants import profile_tabs
from .forms import ProfileForm
from .models import Profile


class ProfileBaseTabView(TemplateView):
    """Profile base view."""

    def get_template_names(self):
        """Dynamically return partial or full tab template based on requests."""
        return f"profiles/tabs/{self.get_url_query()}.html"

    def get_url_query(self):
        """
        Get partial query from htmx request and return partial path.

        Or return full page path
        """
        q = self.request.GET.get("partial_request", None)
        q = q if q in profile_tabs else None  # Prevent invalid requests.
        # Return partial html or full tab profile html path
        return (
            f"partial/{q}"
            if q
            else f"full/{self.request.path.rstrip('/').split('/')[-1]}"
        )

    def get_context_data(self, **kwargs):
        """Provide user profile and profile tab context."""
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, username=self.kwargs["username"])
        context["profile"] = profile
        context["tabs"] = profile_tabs
        context["current_tab"] = self._get_tab_name()
        return context

    def _get_tab_name(self):
        url = self.get_url_query()

        return url.split("/")[-1]


# Profile Tab views
class ProfilePhotosView(ProfileBaseTabView):
    """Profile photos view that handles partial and full request."""


class ProfileAboutView(ProfileBaseTabView):
    """Profile about view that handles partial and full request."""


class ProfileFollowersView(ProfileBaseTabView):
    """Profile Followers view that handles partial and full request."""


class ProfilePostsView(ProfileBaseTabView):
    """Profile Posts view that handles partial and full request."""

    def get_context_data(self, **kwargs):
        """Retrieve only user's posts."""
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, username=self.kwargs["username"])
        user = profile.user
        # self.request.user.posts can't use custom query methods
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
