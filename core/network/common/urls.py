"""Urls for all apps."""

from django.urls import path

from . import views

urlpatterns = [
    path("empty/", views.EmptyView.as_view(), name="empty"),
]
