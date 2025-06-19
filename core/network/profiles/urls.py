"""Profile urls."""

from django.urls import path

from . import views

urlpatterns = [
    path("edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    # Tab views
    path(
        "<str:username>/about/",
        views.ProfileAboutView.as_view(),
        name="profile_about",
    ),
    path(
        "<str:username>/followers/",
        views.ProfileFollowersView.as_view(),
        name="profile_followers",
    ),
    path(
        "<str:username>/posts/",
        views.ProfilePostsView.as_view(),
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
    path(
        "<str:username>/photos/partial/uploads/",
        views.ProfilePhotoUploadsPartialView.as_view(),
        name="partial_photos_uploads",
    ),
    path(
        "<str:username>/photos/partial/albums/",
        views.ProfilePhotoAlbumsPartialView.as_view(),
        name="partial_photos_albums",
    ),
    # Follow
    path("<str:username>/follow/", views.FollowView.as_view(), name="follow"),
    # Following
    path("<str:username>/following/", views.FollowingView.as_view(), name="following"),
]
