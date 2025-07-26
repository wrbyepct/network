from datetime import timedelta

import pytest
from django.utils import timezone
from network.posts.constants import MAX_INCUBATION_MINUTES, MIN_INCUBATION_MINUTES
from network.posts.utils import get_random_publish_time


@pytest.mark.django_db
def test_get_random_publish_time_in_future():
    """Test that get_random_publish_time returns a datetime in the future."""
    future_time = get_random_publish_time()
    assert future_time > timezone.now()


@pytest.mark.django_db
def test_get_random_publish_time_within_range():
    """Test that get_random_publish_time returns a datetime within the specified range."""
    for _ in range(100):  # Run multiple times to account for randomness
        publish_time = get_random_publish_time()
        now = timezone.now()
        min_expected_time = now + timedelta(minutes=MIN_INCUBATION_MINUTES)
        max_expected_time = now + timedelta(minutes=MAX_INCUBATION_MINUTES)
        assert min_expected_time <= publish_time <= max_expected_time
