"""Album views."""

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DetailView, UpdateView

from network.profiles.models import Profile

from .forms import AlbumForm
from .models import Album, AlbumMedia


# Create your views here.
class AlbumDetailView(LoginRequiredMixin, DetailView):
    """Album detail view."""

    context_object_name = "album"
    template_name = "profiles/album_detail.html"
    pk_url_kwarg = "album_pk"

    def get_queryset(self):
        """Provide albums queryset of the requesting user."""
        profile = get_object_or_404(Profile, username=self.kwargs.get("username"))
        return profile.albums.all()


class AlbumCreateView(LoginRequiredMixin, CreateView):
    """View to create Album."""

    template_name = "albums/create.html"
    form_class = AlbumForm
    success_url = reverse_lazy("profile_photos_albums")

    def form_valid(self, form):
        """Associate profile with album."""
        with transaction.atomic():
            form.instance.profile = self.request.user.profile
            resp = super().form_valid(form)
            form.save_medias(self.object)
        return resp

    def get_success_url(self):
        """Get profile album url."""
        profile = self.request.user.profile
        return reverse("profile_photos_albums", args=[profile.username])


class AlbumUpdate(LoginRequiredMixin, UpdateView):
    """View to update album."""

    template_name = "albums/edit.html"
    form_class = AlbumForm

    def get_success_url(self):
        """Get back to the request album detail page."""
        album_pk = self.kwargs.get("album_pk")
        user = self.request.user
        profile = user.profile
        return reverse("album_detail", args=[album_pk, profile.username])

    def get_object(self):
        """Return the specified album owned by the profile."""
        album_pk = self.kwargs.get("album_pk")
        user = self.request.user

        return get_object_or_404(Album, profile=user.profile, pk=album_pk)

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
