"""Profile urls."""

from django.urls import path

from . import views

urlpatterns = [
    path("edit/", views.ProfileEditView.as_view(), name="profile_edit"),
    path(
        "<str:username>/about/",
        views.ProfileAboutView.as_view(),
        name="profile_about",
    ),
    path(
        "<str:username>/photos/",
        views.ProfilePhotosView.as_view(),
        name="profile_photos",
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
]
