"""Post Serives."""

from django.db.models import Max

from .models import PostMedia


class PostMediaService:
    """Service for saving images and videos as PostMedia for a post."""

    @staticmethod
    def save_media(post, images=None, video=None):
        """Save images and/or video as PostMedia linked to a post."""
        media_instances = []

        if images:
            max_order = PostMediaService.get_max_order(post)
            media_instances.extend(
                PostMediaService.create_media(
                    post, image, PostMedia.MediaType.IMAGE, index
                )
                for index, image in enumerate(images, start=max_order + 1)
            )

        if video:
            media_instances.append(
                PostMediaService.create_media(
                    post, video[0], PostMedia.MediaType.VIDEO, order=-1
                )
            )

        PostMedia.objects.bulk_create(media_instances)

    @staticmethod
    def create_media(post, file, media_type, order):
        """Create and return an unsaved PostMedia instance."""
        return PostMedia(
            post=post,
            profile=post.user.profile,
            file=file,
            type=media_type,
            order=order,
        )

    @staticmethod
    def get_max_order(post) -> int:
        """Get highest media order for a post, or 0 if none exists."""
        return (
            PostMedia.objects.filter(post=post).aggregate(Max("order"))["order__max"]
            or 0
        )
