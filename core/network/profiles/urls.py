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
        "<str:username>/followers/",
        views.FollowersView.as_view(),
        name="profile_followers",
    ),
    path(
        "<str:username>/posts/",
        views.PostsView.as_view(),
        name="profile_posts",
    ),
    path(
        "<str:username>/photos/",
        views.PhotosView.as_view(),
        name="profile_photos",
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
    path("<str:username>/follow/", views.FollowView.as_view(), name="follow"),
    # Following
    path("<str:username>/following/", views.FollowingView.as_view(), name="following"),
]
