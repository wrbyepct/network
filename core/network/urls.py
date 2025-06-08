"""User url."""

# ruff: noqa: ERA001
from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("accounts/", include("allauth.urls")),
    path("profiles/", include("network.profiles.urls")),
    path("posts/", include("network.posts.urls")),
]
