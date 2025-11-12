"""Comment custom manager."""

from django.db import models


class CommentQuerySet(models.QuerySet):
    """Comment custom queryset."""

    def prefetched_info_qs(self, user=None):
        """Return all queryset with prefetched profile, children count and if it's liked by the requesting user."""
        from .models import CommentLike

        return (
            self.select_related("user__profile")
            .annotate(
                liked_by_user=models.Exists(
                    CommentLike.objects.filter(
                        user=user, comment_id=models.OuterRef("pk")
                    )
                )
            )
            .annotate(children_count=models.Count("children"))
        )

    def top_level_comment(self, post):
        """Fetch top level comments only."""
        return self.filter(post=post, parent__isnull=True)


class CommentManager(models.Manager):
    """Comment custom manager."""

    def get_queryset(self):
        """Return basic queryset."""
        return CommentQuerySet(model=self.model, using=self._db)

    def prefetched_info_qs(self, user=None):
        """Return all queryset with Prefetched profile data and children."""
        return self.get_queryset().prefetched_info_qs(user)

    def top_level_comments(self, post, user=None):
        """Return top level comment set with prefetched profile data."""
        return self.get_queryset().prefetched_info_qs(user).top_level_comment(post)

    def get_children(self, parent, user=None):
        """Get parent comments."""
        return self.get_queryset().prefetched_info_qs(user).filter(parent=parent)
