"""Post urls."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "create/",
        views.PostCreateView.as_view(),
        name="post_create",
    ),
    path(
        "<uuid:post_id>/modal/",
        views.PostModalView.as_view(),
        name="post_modal",
    ),
    path(
        "<uuid:post_id>/edit/",
        views.PostEditView.as_view(),
        name="post_edit",
    ),
    path(
        "<uuid:post_id>/delete/",
        views.PostDeleteView.as_view(),
        name="post_delete",
    ),
    path(
        "incubating_egg/",
        views.IncubatingEggView.as_view(),
        name="egg",
    ),
    path(
        "<uuid:post_id>/hatched_post/",
        views.HatchedPostView.as_view(),
        name="hatched_post",
    ),
    path(
        "hatch_check/",
        views.PostHatchCheckView.as_view(),
        name="post_hatch_check",
    ),
    path(
        "<uuid:post_id>/like/",
        views.LikePost.as_view(),
        name="post_like",
    ),
]
