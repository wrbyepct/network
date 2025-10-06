import logging

from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from network.posts.models import Post

from .models import Egg

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=Post)
def invalidate_profile_posts_cache(sender, instance, **kwargs):
    logger.info("Post is changing...")
    user_pkid = instance.user.pkid
    key_prefix = f"profile_turties_{user_pkid}"
    cache.delete_pattern(f"*{key_prefix}*")


@receiver([post_save, post_delete], sender=Egg)
def invalidate_profile_nest_cache(sender, instance, **kwargs):
    logger.info("Egg is changing...")
    user_pkid = instance.user.pkid
    key_prefix = f"profile_nest_{user_pkid}"
    cache.delete_pattern(f"*{key_prefix}*")
