"""Service for PostLike. Dealing with liking/unliking a posts."""

from django.contrib.auth.models import AbstractUser
from django.db.models import F

from network.posts.models import Post, PostLike


class PostLikeService:
    """Service class for dealing with like/unlike a post."""

    @staticmethod
    def like_post(post: Post, user: AbstractUser) -> None:
        """
        Increase likes in a post.

        Args:
            post (Post): Post model
            user (AbstractUser): AbstractUser model

        Returns:
            None

        """
        _, created = PostLike.objects.get_or_create(post=post, user=user)
        if created:
            Post.objects.filter(id=post.id).update(like_count=F("like_count") + 1)

    @staticmethod
    def unlike_post(post: Post, user: AbstractUser) -> None:
        """
        Decrease likes in a post.

        Args:
            post (Post): Post model
            user (AbstractUser): AbstractUser model

        Returns:
            None

        """
        deleted, _ = PostLike.objects.filter(post=post, user=user).delete()
        if deleted:
            Post.objects.filter(id=post.id, like_count__gt=0).update(
                like_count=F("like_count") - 1
            )
