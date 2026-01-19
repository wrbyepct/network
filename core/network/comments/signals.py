import logging

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Comment

logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=Comment)
def sync_post_comment_count(sender, instance, **kwargs):
    # Skip UPDATES (post_save with created=False)
    if "created" in kwargs and not kwargs["created"]:
        logger.warning("Comment updated, skipping count sync")
        return

    old_count = instance.post.comment_count
    logger.info(f"Post comment pre-update: {old_count}")

    instance.post.sync_comment_count()
    new_count = instance.post.comment_count

    logger.info(f"Post comment updated: {new_count}")
