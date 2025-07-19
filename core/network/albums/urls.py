"""Album urls."""

from django.urls import path

from . import views

urlpatterns = [
    # Album
    path(
        "<str:username>/paginate/albums/",
        views.AlbumsPaginateView.as_view(),
        name="albums_paginate",
    ),
    path(
        "albums/create/",
        views.AlbumCreateView.as_view(),
        name="album_create",
    ),
    path(
        "albums/<uuid:album_id>/medias/",
        views.AlbumMediasPaginator.as_view(),
        name="album_media_list",
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
    path(
        "albums/<uuid:album_id>/delete/",
        views.AlbumDeleteView.as_view(),
        name="album_delete",
    ),
]
