from datetime import timedelta
from unittest.mock import patch

import pytest
from django.utils import timezone
from model_bakery import baker
from network.posts.models import Post
from network.posts.tasks import publish_post


@pytest.mark.django_db
def test_post_publish_at_field_can_be_none():
    """Test that the publish_at field can be None."""
    post = baker.make(Post, publish_at=None)
    assert post.publish_at is None


@pytest.mark.django_db
def test_post_publish_at_field_can_be_future():
    """Test that the publish_at field can be set to a future datetime."""
    future_time = timezone.now() + timedelta(hours=1)
    post = baker.make(Post, publish_at=future_time)
    assert post.publish_at == future_time


@pytest.mark.django_db
def test_post_set_random_publish_time():
    """Test that set_random_publish_time sets a future publish_at."""
    post = baker.make(Post)
    post.incubate_post()
    assert post.publish_at is not None
    assert post.publish_at > timezone.now()
    # Further check if it's within the random range (already covered by test_utils.py)


#####################
## Test Task Assign #
#####################


@pytest.mark.django_db
def test_post_is_published_default_false():
    """Test that is_published field defaults to False."""
    post = baker.make(Post)
    assert post.is_published is False


@pytest.mark.django_db
@patch("network.posts.tasks.assign_publish_task")
def test_post_save_schedules_task_if_future_publish_at(mock_assign_publish_task):
    """Test that saving a post with future publish_at schedules a task."""
    future_time = timezone.now() + timedelta(hours=1)
    post = baker.make(Post, publish_at=future_time, is_published=False)
    mock_assign_publish_task.return_value = "mock_task_id"
    post.save()
    mock_assign_publish_task.assert_called_once_with(post)
    assert post.celery_task_id == "mock_task_id"


@pytest.mark.django_db
@patch("network.posts.tasks.assign_publish_task")
def test_post_save_does_not_schedule_task_if_no_publish_at(mock_assign_publish_task):
    """Test that saving a post with no publish_at does not schedule a task."""
    post = baker.make(Post, publish_at=None, is_published=False)
    post.save()
    mock_assign_publish_task.assert_not_called()
    assert post.celery_task_id is None


@pytest.mark.django_db
@patch("network.posts.tasks.delete_task")
def test_post_delete_revokes_task(mock_delete_task):
    """Test that deleting a post revokes the scheduled task."""
    post = baker.make(Post, celery_task_id="test_task_id")
    post.delete()
    mock_delete_task.assert_called_once_with("test_task_id")


@pytest.mark.django_db
def test_publish_post_task_sets_is_published_true():
    """Test that the publish_post task sets is_published to True."""
    post = baker.make(
        Post, publish_at=timezone.now() - timedelta(minutes=1), is_published=False
    )
    publish_post(post.id)
    post.refresh_from_db()
    assert post.is_published is True
    assert post.publish_at is not None


@pytest.mark.django_db
def test_publish_post_task_does_not_change_published_post():
    """Test that the publish_post task does not change an already published post."""
    original_publish_at = timezone.now() - timedelta(hours=1)
    post = baker.make(Post, publish_at=original_publish_at, is_published=True)
    publish_post(post.id)
    post.refresh_from_db()
    assert post.is_published is True
    assert post.publish_at == original_publish_at


@pytest.mark.django_db
def test_publish_post_task_handles_non_existent_post():
    """Test that the publish_post task handles a non-existent post gracefully."""
    # No assertion needed, just ensure it doesn't raise an error
    publish_post(99999)
