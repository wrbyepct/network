"""Comment urls."""

from django.urls import path

from . import views

urlpatterns = [
    path(
        "<uuid:post_id>/create/",
        views.CommentCreateView.as_view(),
        name="comment_create",
    )
]
