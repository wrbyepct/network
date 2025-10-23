"""View."""

from allauth.account import app_settings
from allauth.account.utils import complete_signup, perform_login
from allauth.account.views import LoginView, SignupView
from django.http import HttpResponse

from network.posts.views import PostListView


class IndexView(PostListView):
    """Index view."""


class HtmxAuthMixin:
    """Htmx auth mixin."""

    def form_invalid(self, form):
        """Return response with 400."""
        response = super().form_invalid(form)
        if self.request.headers.get("HX-Request") == "true":
            response.status_code = 400

        return response

    def get_htmx_response(self):
        """Return htmx customized response."""
        # If HTMX, return 200 + HX-Redirect; else do a normal redirect
        url = "/"
        if self.request.headers.get("HX-Request") == "true":
            resp = HttpResponse(status=200)
            resp["HX-Redirect"] = url
            return resp
        return url


class CustomSignupView(HtmxAuthMixin, SignupView):
    """Custom Sign up View for dealing sign up after actions."""

    def form_valid(self, form):
        """Return empty response and redirect the logged user."""
        user = form.save(self.request)
        complete_signup(
            self.request, user, app_settings.EMAIL_VERIFICATION, self.get_success_url()
        )

        return self.get_htmx_response()


class CustomLoginView(HtmxAuthMixin, LoginView):
    """Custom Sign up View for dealing sign up after actions."""

    def form_valid(self, form):
        """Return empty response and redirect the logged user."""
        user = form.user
        perform_login(
            self.request,
            user,
            email_verification=app_settings.EMAIL_VERIFICATION,
            redirect_url=self.get_success_url(),
        )
        return self.get_htmx_response()
