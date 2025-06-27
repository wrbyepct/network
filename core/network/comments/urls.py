"""Comment urls."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "<uuid:post_id>/create/",
        views.CommentCreateView.as_view(),
        name="comment_create",
    ),
    path(
        "<uuid:comment_id>/edit/",
        views.CommentUpdateView.as_view(),
        name="comment_edit",
    ),
    path(
        "<uuid:comment_id>/delete/",
        views.CommentDeleteView.as_view(),
        name="comment_delete",
    ),
]
