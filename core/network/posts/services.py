"""Post Serives."""

import random

from django.core.cache import cache
from django.db import transaction
from django.db.models import Max

from .models import PostMedia
from .tasks import assign_publish_task
from .utils import get_random_publish_time, get_random_timeout


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


class IncubationService:
    """Service for incubate a post."""

    default_egg_url = "media/defaults/regular_eggs/egg5.gif"
    EGG_TYPES = ["regular_eggs", "special_eggs"]
    WEIGHTS = [0.9, 0.1]

    @staticmethod
    def get_random_egg_img_index():
        """Return random egg img url."""
        return random.randint(0, 8)

    @staticmethod
    def get_random_egg_type():
        """Return random egg img url."""
        return random.choices(
            IncubationService.EGG_TYPES,
            weights=IncubationService.WEIGHTS,
            k=1,
        )[0]

    @staticmethod
    def get_random_egg_url():
        """Return a random egg url."""
        egg_num = IncubationService.get_random_egg_img_index()
        egg_type = IncubationService.get_random_egg_type()
        return f"media/defaults/{egg_type}/egg{egg_num}.gif"

    @staticmethod
    def incubate_post(post, egg_url):
        """
        Incucbate a post.

        1. Set a publish time for post
        2. Schedule publish time
        3. Save incubating check in cache.
        """
        timeout = get_random_timeout()
        with transaction.atomic():
            post.publish_at = get_random_publish_time(timeout)
            post.celery_task_id = assign_publish_task(post)
            IncubationService.set_incubating_egg_url(post.user.id, egg_url, timeout)
            IncubationService.set_incubating_post_id(post.user.id, post.id, timeout)
            post.save(update_fields=["publish_at", "celery_task_id"])

    @staticmethod
    def set_incubating_post_id(user_id, post_id, timeout):
        """Set incubating post id."""
        key = IncubationService.cache_key(user_id, "post_id")
        cache.set(key, post_id, timeout=timeout)

    @staticmethod
    def get_incubating_post_id(user_id):
        """Get incubating post id."""
        key = IncubationService.cache_key(user_id, "post_id")
        return cache.get(key)

    @staticmethod
    def set_incubating_egg_url(user_id, egg_url, timeout):
        """Set post incubating url timeout cache."""
        key = IncubationService.cache_key(user_id, "egg")
        cache.set(key, egg_url, timeout=timeout)

    @staticmethod
    def get_incubating_egg_url(user_id):
        """Get post incubating url check data."""
        key = IncubationService.cache_key(user_id, "egg")
        return cache.get(key)

    @staticmethod
    def cache_key(user_id, suffix):
        """Incubation cache key."""
        return f"incubating:{suffix}:{user_id}"
