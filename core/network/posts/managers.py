"""Post mangers."""

from django.db import models


class PostQuerySet(models.QuerySet):
    """Customized Post queryset."""

    def with_media(self):
        """Prefetch with medias."""
        return self.prefetch_related("medias")

    def by_user(self, user):
        """Filter post by user."""
        return self.filter(user=user)


class PostManger(models.Manager):
    """Post Manager."""

    def get_queryset(self):
        """Filter posts by user."""
        return PostQuerySet(model=self.model, using=self._db)

    def with_media(self):
        """Optimized post search query when querying with 'medias'."""
        return self.get_queryset().with_media()
