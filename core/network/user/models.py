"""User Model."""

from uuid import uuid4

from django.contrib.auth.models import AbstractUser
from django.db import models

from .managers import CustomUserManager


class User(AbstractUser):
    """User model."""

    pkid = models.BigAutoField(
        primary_key=True,
        editable=False,
    )  # Primary key will make sure it's unqiue
    id = models.UUIDField(default=uuid4, unique=True, editable=False)
    username = None
    email = models.EmailField(unique=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()
