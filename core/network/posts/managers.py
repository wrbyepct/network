"""Post mangers."""

from django.db import models


class PostQuerySet(models.QuerySet):
    """Customized Post queryset."""

    def for_list_data(self, user=None):
        """Select related profile."""
        from network.comments.models import Comment

        from .models import PostLike, PostMedia

        return self.select_related("user__profile", "egg").prefetch_related(
            "likes",  # all likes
            models.Prefetch(
                "likes",
                queryset=PostLike.objects.filter(user=user),
                to_attr="user_likes",
            ),  # liked by requesting user
            models.Prefetch(
                "medias",
                queryset=PostMedia.objects.order_by("order"),
                to_attr="ordered_medias",
            ),
            models.Prefetch(
                "comments",  # all comments with prefetched info
                queryset=Comment.objects.prefetched_info_qs(user),
            ),
            models.Prefetch(
                "comments",
                queryset=Comment.objects.prefetched_info_qs(user).filter(
                    parent__isnull=True
                ),
                to_attr="top_level_comments",
            ),  # top level comments
        )

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

    def published(self, user=None):
        """Return only published posts with necessary data."""
        return self.get_queryset().for_list_data(user).published()
