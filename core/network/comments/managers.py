"""Comment custom manager."""

from django.db import models


class CommentQuerySet(models.QuerySet):
    """Comment custom queryset."""

    def fetch_profile_data(self):
        """Fetch profile data by join profile table."""
        return self.select_related("user__profile")

    def top_level_comment(self, post):
        """Fetch top level comments only."""
        return self.filter(post=post, parent__isnull=True)


class CommentManager(models.Manager):
    """Comment custom manager."""

    def get_queryset(self):
        """Return basic queryset."""
        return CommentQuerySet(model=self.model, using=self._db)

    def top_level_for(self, post):
        """Return top level comment set with prefetched profile data."""
        return self.get_queryset().fetch_profile_data().top_level_comment(post)

    def get_children(self, parent):
        """Get parent comments."""
        return self.get_queryset().fetch_profile_data().filter(parent=parent)
