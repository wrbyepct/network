"""Profile custom mixins."""

from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string

from .constants import photo_tabs, profile_tabs
from .models import Profile


class ProfileTabMixin:
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

    def get_tab_template_path(self):
        """Dynamically return full or partial template path."""
        return f"profiles/tabs/{self.get_sub_tab_template_path()}.html"

    def get_sub_tab_template_path(self):
        """Dynamically return tab template sub path based on request path."""
        request_page_str = self.request.path.rstrip("/").split("/")[-1]

        return (
            f"partial/{request_page_str}"
            if self.is_partial_request()
            else f"full/{request_page_str}"
        )

    def is_partial_request(self):
        """Check if request is partial or full for profile tab request."""
        return self.request.GET.get("is_partial_request", None) == "true"


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

    def get_template_names(self):
        """Get partial template path if partial query exists, or return default full page."""
        if self.photo_partial_key:
            return self.get_photo_partial_template_path()
        return super().get_template_names()

    def get_partial_rendered_string(self, context):
        """Get partial photo tab html string."""
        return render_to_string(
            self.get_photo_partial_template_path(),
            {**context, "request": self.request},
        )

    def get_photo_partial_template_path(self):
        """Get partial photo tab template path."""
        return self.PHOTO_PARTIALS[self.resolved_tab]
