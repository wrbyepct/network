# Create your views here.
"""Profile views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Exists, OuterRef
from django.shortcuts import get_object_or_404, render
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_headers
from django.views.generic import (
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from network.common.mixins import SetHtmxAlertTriggerMixin
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
        self.profile = get_object_or_404(
            Profile.objects.select_related("user"),
            username=kwargs.get("username"),
        )

        return super().dispatch(request, *args, **kwargs)

    def get_template_names(self):
        """Provide partial or full template based on partial request or not."""
        _, tab = self.request.path.rstrip("/").rsplit("/", 1)

        if self.request.htmx:
            return [f"profiles/tabs/partial/{tab}.html"]
        return [f"profiles/tabs/full/{tab}.html"]

    def get_context_data(self, **kwargs):
        """Provide context data based on partial request."""
        context = super().get_context_data(**kwargs)
        if not self.request.htmx:
            # Provide tabs info in full page request
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


@method_decorator(cache_page(900), name="dispatch")
@method_decorator(vary_on_headers("HX-Request"), name="dispatch")
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


@method_decorator(cache_page(900), name="dispatch")
@method_decorator(vary_on_headers("HX-Request"), name="dispatch")
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
        return PostMedia.objects.filter(profile=self.profile).select_related("post")


@method_decorator(cache_page(900), name="dispatch")
@method_decorator(vary_on_headers("HX-Request"), name="dispatch")
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

    @method_decorator(vary_on_headers("HX-Request"))
    def dispatch(self, request, *args, **kwargs):
        """Cache dispatch with username as key."""
        user_pkid = request.user.pkid
        key_prefix = f"profile_posts_{user_pkid}"

        return cache_page(900, key_prefix=key_prefix)(super().dispatch)(
            request, *args, **kwargs
        )

    def get_queryset(self):
        """Get prefetched post queryset by the profile user."""
        profile_user = self.profile.user
        requesting_user = self.request.user
        return Post.objects.published(requesting_user).by_user(user=profile_user)


@method_decorator(cache_page(900), name="dispatch")
@method_decorator(vary_on_headers("HX-Request"), name="dispatch")
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


@method_decorator(cache_page(900), name="dispatch")
@method_decorator(vary_on_headers("HX-Request"), name="dispatch")
class AboutView(LoginRequiredMixin, ProfileTabsBaseMixin, TemplateView):
    """Profile about view that handles partial and full request."""

    current_tab = "about"

    def get_context_data(self, **kwargs):
        """Inject user activity status in context."""
        context = super().get_context_data(**kwargs)

        context["sub_tab"] = self.request.GET.get("sub_tab", "story")
        profile = self.profile
        eggs_count = profile.get_eggs_qunt()

        context.update(eggs_count)

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

        # Follower/following profile need user id to retrieve activity data
        if self.follow_type == "followers":
            return profile.followers.select_related("user").annotate(
                mutual_followed=Exists(profile.following.filter(pk=OuterRef("pk")))
            )

        return profile.following.select_related("user")

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
class FollowView(SetHtmxAlertTriggerMixin, View):
    """View to follow/unfollow a user's profile."""

    def post(self, request, *args, **kwargs):
        """Follow a profile and return success message."""
        to_profile = get_object_or_404(Profile, username=kwargs.get("username"))
        profile = request.user.profile

        has_followed = profile.has_followed(to_profile)

        if not has_followed:
            profile.follow(to_profile)
            message = f"You followed {to_profile.username}!"

        else:
            profile.unfollow(to_profile)
            message = f"Unfollowed {to_profile.username}."

        resp = render(
            self.request, "profiles/tabs/partial/follow.html", {"profile": profile}
        )

        return self.set_htmx_trigger(
            resp=resp,
            event_name="follow-success",
            message=message,
        )


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
        context = {"profile_updated": True, "form": form}
        return render(self.request, self.template_name, context)
