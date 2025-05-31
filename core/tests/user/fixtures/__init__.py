"""User tests fixtures."""

import pytest
from pytest_factoryboy import register

from .factories import UserFactory

register(UserFactory)


@pytest.fixture
def say_hello():
    return 1
