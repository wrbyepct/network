"""Album form."""

from django import forms

from network.common.fields import MultipleFileField
from network.common.mixins import MediaMixin
from network.common.validators import validate_media_extension

from .models import Album, AlbumMedia


class AlbumForm(MediaMixin, forms.ModelForm):
    """Album form."""

    medias = MultipleFileField(required=False, validators=[validate_media_extension])

    class Meta:
        model = Album
        fields = ["name"]

    def save_medias(self, album):
        """Save valid uploaded media to album."""
        medias = self.cleaned_data.get("medias")

        if medias:
            max_order = self.get_max_order(album)
            AlbumMedia.objects.bulk_create(
                [
                    AlbumMedia(
                        album=album,
                        file=media,
                        order=index,
                        type=self.get_media_type(media),
                    )
                    for index, media in enumerate(medias, start=max_order + 1)
                ]
            )
