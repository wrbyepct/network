"""User manager."""

from django.contrib.auth.models import BaseUserManager


class CustomUserManager(BaseUserManager):
    """Custom user manager to create user only without username."""

    def create_user(self, email, password, **extra_fields):
        """Create user."""
        if not email:
            message = "Email must be set."
            raise ValueError(message)

        email = self.normalize_email(email)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        """Create super user, with is_staff is_superuser set to True."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            message = "is_staff must be True for super user"
            raise ValueError(message)
        if not extra_fields.get("is_superuser"):
            message = "is_superuser must be True for super user"
            raise ValueError(message)

        return self.create_user(email, password, **extra_fields)
