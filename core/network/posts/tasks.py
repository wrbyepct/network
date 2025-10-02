"""Celery tasks for post apps."""

import json
import logging

import redis
from celery import shared_task
from django.core.files.storage import default_storage
from django.utils.timezone import now
from project4.celery import app

logger = logging.getLogger(__name__)

# Initialize Redis client
# Assuming Redis is accessible at 'redis' hostname and default port 6379
# This should match the Redis service name in docker-compose.yml
redis_client = redis.StrictRedis(host="redis", port=6379, db=0)

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

        # Publish to Redis channel
        message = {"post_id": str(post.id)}
        redis_client.publish("post_hatch_events", json.dumps(message))
        logger.info(f"Published hatch event for post {post.id} to Redis.")

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


@shared_task
def save_post_media_task(post_id, image_paths, video_paths):
    """Task to save post uploade media."""
    from .models import Post
    from .services import PostMediaService

    post = Post.objects.get(id=post_id)

    # Reopen files from storage
    images = [default_storage.open(path, "rb") for path in image_paths]
    videos = [default_storage.open(path, "rb") for path in video_paths]

    PostMediaService.save_media(post, images, videos)

    # Optional: clean up temp files if you don't need them anymore
    for path in image_paths + video_paths:
        default_storage.delete(path)
