"""Post mangers."""

from django.db import models


class PostQuerySet(models.QuerySet):
    """Customized Post queryset."""

    def with_profile(self):
        """Select related profile."""
        return self.select_related("user__profile")

    def with_media(self):
        """Prefetch with medias."""
        return self.prefetch_related("medias")

    def by_user(self, user):
        """Filter post by user."""
        return self.filter(user=user)

    def published(self):
        """Return only published posts."""
        return self.filter(is_published=True)


class PostManager(models.Manager):
    """Post Manager."""

    def get_queryset(self):
        """Filter posts by user."""
        return PostQuerySet(model=self.model, using=self._db)

    def with_media(self):
        """Optimized post search query when querying with 'medias'."""
        return self.get_queryset().with_media()

    def for_list_data(self):
        """Return optimized posts with medias, profile and comment data."""
        return self.get_queryset().with_media().with_profile()

    def published(self):
        """Return only published posts with necessary data."""
        return self.for_list_data().published()
