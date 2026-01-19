import logging

from django.db.models import F
from django.db.models.functions import Greatest
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import Comment

logger = logging.getLogger(__name__)


@receiver([post_save], sender=Comment)
def increment_comment_count(sender, instance, created, **kwargs):
    if created:
        post = instance.post  # Gets from cache or DB
        post.comment_count = F("comment_count") + 1

        # Cacheops auto-invalidates on save(
        post.save(update_fields=["comment_count"])


@receiver([post_delete], sender=Comment)
def decrement_comment_count(sender, instance, **kwargs):
    post = instance.post  # Gets from cache or DB
    post.comment_count = Greatest(F("comment_count") - 1, 0)

    # Cacheops auto-invalidates on save()
    post.save(update_fields=["comment_count"])
