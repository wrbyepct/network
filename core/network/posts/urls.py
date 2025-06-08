"""Post urls."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "all/",
        views.PostListView.as_view(),
        name="post_list",
    ),
    path(
        "create/",
        views.PostCreateView.as_view(),
        name="post_create",
    ),
]
