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
        views.ProfilePhotosView.as_view(),
        name="profile_photos",
    ),
    path(
        "<str:username>/photos_albums/",
        views.ProfilePhotoAlbumFullView.as_view(),
        name="profile_photos_albums",
    ),
    # Album
    path(
        "albums/create/",
        views.AlbumCreateView.as_view(),
        name="album_create",
    ),
    path(
        "albums/<int:album_pk>/<str:username>/detail/",
        views.AlbumDetailView.as_view(),
        name="album_detail",
    ),
    path(
        "albums/<int:album_pk>/edit/",
        views.AlbumUpdate.as_view(),
        name="album_edit",
    ),
    # Follow
    path("<str:username>/follow/", views.FollowView.as_view(), name="follow"),
    # Following
    path("<str:username>/following/", views.FollowingView.as_view(), name="following"),
]
