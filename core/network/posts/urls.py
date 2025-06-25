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
    path(
        "<uuid:post_id>/detail/",
        views.PostDetailView.as_view(),
        name="post_detail",
    ),
    path(
        "edit/<uuid:post_id>/",
        views.PostEditView.as_view(),
        name="post_edit",
    ),
    path(
        "delete/<uuid:post_id>/",
        views.PostDeleteView.as_view(),
        name="post_delete",
    ),
    path(
        "like/<uuid:post_id>",
        views.LikePost.as_view(),
        name="post_like",
    ),
]
