"""Album views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from network.common.mixins import SetOwnerProfileMixin
from network.profiles.models import Profile

from .forms import AlbumForm
from .models import Album, AlbumMedia


class AlbumsPaginateView(ListView):
    """Album paginate view that handle partial albums paginate retreive."""

    template_name = "albums/album_paginator.html"
    context_object_name = "albums"
    paginate_by = 10

    def dispatch(self, request, *args, **kwargs):
        """Save profile for later use."""
        self.profile = get_object_or_404(
            Profile.objects.select_related("user"),
            username=self.kwargs.get("username"),
        )
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Get albums owned by the profile."""
        return (
            Album.objects.filter(profile=self.profile)
            .select_related("profile", "profile__user")
            .prefetch_related("medias")
            .annotate(medias_count=Count("medias"))
        )

    def get_context_data(self, **kwargs):
        """Inject profile into context."""
        context = super().get_context_data(**kwargs)
        context["profile"] = self.profile
        return context


class AlbumMediasPaginatorView(ListView):
    """Album Photos paginator view."""

    context_object_name = "medias"
    template_name = "albums/media_paginator.html"
    paginate_by = 10

    def get_queryset(self):
        """Get album medias paginated by 10."""
        self.album = get_object_or_404(Album, id=self.kwargs.get("album_id"))
        return self.album.medias.all()

    def get_context_data(self, **kwargs):
        """Inject album instance in context."""
        context = super().get_context_data(**kwargs)
        context["album"] = self.album
        return context


# Create your views here.
class AlbumDetailView(LoginRequiredMixin, DetailView):
    """Album detail view."""

    context_object_name = "album"
    template_name = "albums/detail.html"

    def get_object(self, queryset=None):
        """Directly return the album obect."""
        profile = get_object_or_404(Profile, username=self.kwargs.get("username"))

        return get_object_or_404(Album, pk=self.kwargs.get("album_pk"), profile=profile)


class AlbumCreateView(SetOwnerProfileMixin, LoginRequiredMixin, CreateView):
    """View to create Album."""

    template_name = "albums/create.html"
    form_class = AlbumForm
    success_url = reverse_lazy("profile_photos_albums")

    def form_valid(self, form):
        """Associate profile with album."""
        with transaction.atomic():
            form.instance.profile = (
                self._profile
            )  # associate the profile with the album
            resp = super().form_valid(form)
            form.save_medias(self.object)
        return resp

    def get_success_url(self):
        """Get profile album url."""
        return reverse_lazy("profile_photos_albums", args=[self._profile.username])


class AlbumUpdate(SetOwnerProfileMixin, LoginRequiredMixin, UpdateView):
    """View to update album."""

    template_name = "albums/edit.html"
    form_class = AlbumForm

    def get_success_url(self):
        """Get back to the request album detail page."""
        album_pk = self.kwargs.get("album_pk")

        return reverse_lazy("album_detail", args=[album_pk, self._profile.username])

    def get_object(self):
        """Return the specified album owned by the profile."""
        album_pk = self.kwargs.get("album_pk")

        return get_object_or_404(Album, profile=self._profile, pk=album_pk)

    def get_context_data(self, **kwargs):
        """Provide existing medias in album in context."""
        context = super().get_context_data(**kwargs)
        album = self.object
        context["medias"] = album.medias.all()
        return context

    def form_valid(self, form):
        """Handle delete requested media and save new ones."""
        delete_ids = self.request.POST.getlist("delete_media")
        with transaction.atomic():
            AlbumMedia.objects.filter(id__in=delete_ids).delete()
            resp = super().form_valid(form)
            form.save_medias(self.object)
        return resp


class AlbumDeleteView(SetOwnerProfileMixin, DeleteView):
    """View to delete a album owned by the requesting user."""

    def get_success_url(self):
        """Go back to albums pages of the requesting profile."""
        return reverse_lazy("profile_photos_albums", args=[self._profile.username])

    def get_object(self, queryset=None):
        """Get the album owned by requesting user."""
        return get_object_or_404(
            Album, id=self.kwargs.get("album_id"), profile=self._profile
        )
