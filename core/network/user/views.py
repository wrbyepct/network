"""View."""

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, RedirectView, TemplateView

from .forms import SignupForm


class IndexView(TemplateView):
    """Index view."""

    template_name = "network/index.html"


class LoginView(DjangoLoginView):
    """Login view."""

    template_name = "network/login.html"
    redirect_authenticated_user = True
    next_page = reverse_lazy("index")

    def form_invalid(self, form):
        """Provide error to frontend if form is invalid."""
        messages.error(self.request, "Invalid username or password.")
        return super().form_invalid(form)


class LogoutView(RedirectView):
    """Logout View."""

    pattern_name = "index"

    def get(self, request, *args, **kwargs):
        """Log out the user."""
        logout(request)
        return super().get(request, *args, **kwargs)


class RegisterView(CreateView):
    """Register view."""

    template_name = "network/register.html"
    form_class = SignupForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        """Save user and login after form is valid."""
        resp = super().form_valid(
            form
        )  # This function will create user instance from the form
        user = self.object
        login(self.request, user=user)
        return resp
