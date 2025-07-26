"""Celery tasks for post apps."""

from celery import shared_task
from project4.celery import app


@shared_task
def publish_post(post_id):
    """Celery task to publish post by setting is_publish to True."""
    from .models import Post

    """Set a post's `published_at` to the current time."""
    try:
        post = Post.objects.get(pk=post_id)
        if not post.published_at:
            post.is_published = True
            post.save(update_fields=["is_published"])
    except Post.DoesNotExist:
        # The post may have been deleted before the task ran.
        pass


def assign_publish_task(post):
    """Assing publish post task and return task id."""
    # If the task has already been scheduled, revoke it
    if post.celery_task_id:
        delete_task(post.id)

    # Schedule the new task
    task = publish_post.apply_async(args=[post.id], eta=post.publish_at)
    return task.id


def delete_task(task_id):
    """Delete task by id."""
    app.control.revoke(task_id)
