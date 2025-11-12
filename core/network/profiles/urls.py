"""Profile urls."""

from django.urls import path

from . import views

urlpatterns = [
    path("edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    # Tab views
    path(
        "<str:username>/about/",
        views.AboutView.as_view(),
        name="profile_about",
    ),
    path(
        "<str:username>/nest/",
        views.NestView.as_view(),
        name="profile_nest",
    ),
    path(
        "<str:username>/tab/follow/",
        views.FollowTabView.as_view(),
        name="profile_follow",
    ),
    path(
        "<str:username>/posts/",
        views.PostsView.as_view(),
        name="profile_turties",
    ),
    path(
        "<str:username>/photos/",
        views.PhotosView.as_view(),
        name="profile_shells",
    ),
    path(
        "<str:username>/photos/uploads/",
        views.PhotosUploadsView.as_view(),
        name="profile_photos_uploads",
    ),
    path(
        "<str:username>/photos/albums/",
        views.PhotosAlbumsView.as_view(),
        name="profile_photos_albums",
    ),
    # Follow
    path(
        "<str:username>/follow/",
        views.FollowView.as_view(),
        name="follow",
    ),
    path(
        "<str:username>/followers/",
        views.FollowersPaginatorView.as_view(),
        name="followers_paginator",
    ),
    path(
        "<str:username>/following/",
        views.FollowingPaginatorView.as_view(),
        name="following_paginator",
    ),
]
