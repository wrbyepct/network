# Create your views here.
"""Profile views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from network.posts.forms import AlbumForm
from network.posts.models import Post

from .constants import photo_tabs, profile_tabs
from .forms import ProfileForm
from .models import Profile


class TabMixin:
    """Provide tab context data and handle partial & full tab page request."""

    profile_tab = None
    active_tab = None

    def get_tab_context(self):
        """Get tab context. Update photo tab context if it's photo tab."""
        context = {
            "tabs": profile_tabs,
            "current_tab": self.profile_tab,
        }
        if self.profile_tab == "photos":
            context.update(
                {
                    "photo_tabs": photo_tabs,
                    "current_photo_tab": self.active_tab,
                }
            )
        return context

    def is_partial_request(self):
        """Check if request is partial or full for profile tab request."""
        return self.request.GET.get("is_partial_request", None) == "true"

    def get_sub_tab_template_path(self):
        """Dynamically return tab template sub path."""
        request_page_str = self.request.path.rstrip("/").split("/")[-1]

        return (
            f"partial/{request_page_str}"
            if self.is_partial_request()
            else f"full/{request_page_str}"
        )

    def get_tab_template_path(self):
        """Dynamically return full or partial template path."""
        return f"profiles/tabs/{self.get_sub_tab_template_path()}.html"


class ProfileContextMixin:
    """Mixin to provide profile to context."""

    def dispatch(self, request, *args, **kwargs):
        """Set profile instance on receiving request."""
        self.set_profile()
        return super().dispatch(request, *args, **kwargs)

    def set_profile(self):
        """Get profile instance from argument or return 404."""
        self._profile = get_object_or_404(Profile, username=self.kwargs["username"])

    def get_profile_context(self):
        """Return get_profile_context."""
        return {"profile": self._profile}


class ProfileBaseTabView(ProfileContextMixin, TabMixin, TemplateView):
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


#####################
# Profile Tab views #
#####################


class PartialPhotoTabMixin:
    """Mixin to handle return partial template path for partial request."""

    PHOTO_PARTIALS = {
        "uploads": "profiles/tabs/partial/photo_partials/uploads.html",
        "albums": "profiles/tabs/partial/photo_partials/albums.html",
    }

    def dispatch(self, request, *args, **kwargs):
        """Set photo partial key if any. And key for partial template."""
        self.photo_partial_key = self.get_photo_partial_key()
        self.resolved_tab = self.photo_partial_key or self.active_tab
        return super().dispatch(request, *args, **kwargs)

    def get_photo_partial_key(self):
        """Get photo tabs partial key in request. Return None if not found or not in allowed valid keys."""
        query = self.request.GET.get("photo_partial_key")

        return query if query in photo_tabs else None

    def get_partial_rendered_string(self, context):
        """Get partial photo tab html string."""
        return render_to_string(
            self.get_photo_partial_template_path(),
            {**context, "request": self.request},
        )

    def get_photo_partial_template_path(self):
        """Get partial photo tab template path."""
        return self.PHOTO_PARTIALS[self.resolved_tab]


# Base photo view.
class ProfilePhotoBaseView(PartialPhotoTabMixin, ProfileBaseTabView):
    """Base view photo page."""

    profile_tab = "photos"

    def get_template_names(self):
        """Get partial template path if partial query exists, or return default full page."""
        if self.photo_partial_key:
            return self.get_photo_partial_template_path()
        return super().get_template_names()

    def get_context_data(self, **kwargs):
        """Provide photo tabs constant for frontend."""
        context = super().get_context_data(**kwargs)

        if self.photo_partial_key is None:  # Fallbacks to full page request
            # Render data for photo_content block in partial photos.html
            context["photo_content"] = self.get_partial_rendered_string(context)
        return context


# Photo uploads view
class ProfilePhotosView(ProfilePhotoBaseView):
    """Profile photos view that handles partial and full request."""

    active_tab = "uploads"


# Photo albums view
class ProfilePhotoAlbumFullView(ProfilePhotoBaseView):
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


class AlbumDetailView(LoginRequiredMixin, DetailView):
    """Album detail view."""

    context_object_name = "album"
    template_name = "profiles/album_detail.html"
    pk_url_kwarg = "album_pk"

    def get_queryset(self):
        """Provide albums queryset of the requesting user."""
        profile = get_object_or_404(Profile, username=self.kwargs.get("username"))
        return profile.albums.all()


class AlbumCreateView(LoginRequiredMixin, CreateView):
    """View to create Album."""

    template_name = "albums/create.html"
    form_class = AlbumForm
    success_url = reverse_lazy("profile_photos_albums")

    def form_valid(self, form):
        """Associate profile with album."""
        with transaction.atomic():
            form.instance.profile = self.request.user.profile
            resp = super().form_valid(form)
            form.save_medias(self.object)
        return resp

    def get_success_url(self):
        """Get profile album url."""
        profile = self.request.user.profile
        return reverse("profile_photos_albums", args=[profile.username])


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
