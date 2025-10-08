import logging

from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from network.posts.models import Post, PostMedia

from .models import Egg

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=Post)
def invalidate_profile_posts_cache(sender, instance, **kwargs):
    logger.info("Post is changing...")
    username = instance.user.profile.username
    key = make_template_fragment_key("profile_posts", [username])
    cache.delete(key)


@receiver([post_save, post_delete], sender=Egg)
def invalidate_profile_nest_cache(sender, instance, **kwargs):
    logger.info("Egg is changing...")
    username = instance.user.profile.username
    key = make_template_fragment_key("profile_nest", [username])

    cache.delete(key)


@receiver([post_save, post_delete], sender=PostMedia)
def invalidate_post_media_cache(sender, instance, **kwargs):
    username = instance.profile.username
    key = make_template_fragment_key("profile_uploads", [username])
    cache.delete(key)
