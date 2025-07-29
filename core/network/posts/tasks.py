"""Celery tasks for post apps."""

import logging

from celery import shared_task
from django.utils.timezone import now
from project4.celery import app

logger = logging.getLogger(__name__)


@shared_task
def publish_post(post_id):
    """Celery task to publish post by setting is_publish to True."""
    from .models import Post  # Import inside to avoid circular imports

    try:
        post = Post.objects.get(id=post_id)

        post.is_published = True
        post.save(update_fields=["is_published"])

        logger.info(f"Post publish time: {post.publish_at}")
        logger.info(f"Current time: {now()}")

    except Post.DoesNotExist:
        # Optionally log a warning here
        logger.warning(f"Post id {post_id} does not exist.")


# TODO Consider separating tasks and tasks manager logic
def assign_publish_task(post):
    """Assing publish post task and return task id."""
    # If the task has already been scheduled, revoke it
    if post.celery_task_id:
        delete_task(post.celery_task_id)

    # Schedule the new task
    task = publish_post.apply_async(args=[post.id], eta=post.publish_at)
    return task.id


def delete_task(task_id):
    """Delete task by id."""
    app.control.revoke(task_id)
