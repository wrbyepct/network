# Create your views here.
"""Profile views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import TemplateView, UpdateView

from .constants import profile_tabs
from .forms import ProfileForm
from .models import Profile


class ProfileEditView(LoginRequiredMixin, UpdateView):
    """Profile creation view."""

    template_name = "profiles/edit.html"
    form_class = ProfileForm
    success_url = reverse_lazy("profile_edit")

    def get_object(self, queryset=None):
        """Return the requesting user's Profile."""
        return self.request.user.profile


class ProfileBaseTabView(TemplateView):
    """Profile base view."""

    def get_url_query(self):
        """Get partial query from htmx request."""
        q = self.request.GET.get("query", None)
        q = q if q in profile_tabs else None
        return (
            f"partial/{q}"
            if q
            else f"full/{self.request.path.rstrip('/').split('/')[-1]}"
        )

    def get_template_names(self):
        """Dynamically return partial or full template."""
        return f"profiles/tabs/{self.get_url_query()}.html"

    def get_context_data(self, **kwargs):
        """Provide user profile and profile tab context."""
        context = super().get_context_data(**kwargs)
        profile = get_object_or_404(Profile, username=self.kwargs["username"])
        context["profile"] = profile
        context["tabs"] = profile_tabs
        return context


# Tab views
class ProfilePhotosView(ProfileBaseTabView):
    """Profile photos view."""


class ProfileAboutView(ProfileBaseTabView):
    """Profile about view."""


class ProfileFollowersView(ProfileBaseTabView):
    """Profile Followers view."""


class ProfilePostsView(ProfileBaseTabView):
    """Profile Posts view."""
