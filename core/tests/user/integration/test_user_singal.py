"""Test user signals."""

import pytest

pytestmark = pytest.mark.django_db


def test_health(say_hello):
    assert say_hello == 1


def test_user_signal__create_user_also_create_profile(user_factory):
    user = user_factory.create()
    profile = user.profile
    assert profile is not None
    assert profile.username == user.email
