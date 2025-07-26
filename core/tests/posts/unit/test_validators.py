from datetime import timedelta

import pytest
from django.core.exceptions import ValidationError
from django.utils import timezone
from model_bakery import baker
from network.posts.constants import MIN_INCUBATION_MINUTES
from network.posts.models import Post
from network.posts.validators import validate_publish_time


@pytest.mark.django_db
def test_validate_publish_time_raises_error_for_past_publish_at():
    """Test that validate_publish_time raises ValidationError if publish_at is in the past."""
    post = baker.make(Post)
    post.created_at = timezone.now() - timedelta(hours=2)  # Set created_at in the past
    post.publish_at = timezone.now() - timedelta(hours=2)  # Set publish_at in the past
    with pytest.raises(
        ValidationError,
        match="Publish time must be at least 20 minutes after creation.",
    ):
        validate_publish_time(post)


@pytest.mark.django_db
def test_validate_publish_time_raises_error_for_too_soon_publish_at():
    """Test that validate_publish_time raises ValidationError if publish_at is less than MIN_INCUBATION_MINUTES after created_at."""
    post = baker.make(Post)
    post.created_at = timezone.now()
    post.publish_at = timezone.now() + timedelta(
        minutes=MIN_INCUBATION_MINUTES - 1
    )  # 1 minute less than min incubation
    with pytest.raises(
        ValidationError,
        match="Publish time must be at least 20 minutes after creation.",
    ):
        validate_publish_time(post)


@pytest.mark.django_db
def test_validate_publish_time_valid_publish_at():
    """Test that validate_publish_time does not raise error for valid publish_at."""
    post = baker.make(Post)
    post.created_at = timezone.now()
    post.publish_at = timezone.now() + timedelta(
        minutes=MIN_INCUBATION_MINUTES + 1
    )  # 1 minute more than min incubation
    try:
        validate_publish_time(post)
    except ValidationError:
        pytest.fail("ValidationError raised for a valid publish_at time.")
