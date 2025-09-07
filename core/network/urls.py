"""User url."""

# ruff: noqa: ERA001
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("accounts/signup/", views.CustomSignupView.as_view(), name="account_signup"),
    path("accounts/login/", views.CustomLoginView.as_view(), name="account_login"),
    path("accounts/", include("allauth.urls")),
    path("profiles/", include("network.profiles.urls")),
    path("posts/", include("network.posts.urls")),
    path("albums/", include("network.albums.urls")),
    path("comments/", include("network.comments.urls")),
]
