"""Profile models."""

from django.conf import settings
from django.core.exceptions import BadRequest
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from network.common.models import TimestampedModel
from network.tools.media import generate_file_path


class FollowMixin:
    """Functions for follow and unflow a profile."""

    def follow(self, profile):
        """Follow a profile."""
        if profile.id == self.id:
            message = "You cannot follow yourself."
            raise BadRequest(message)

        profile.following.add(profile)

    def unfollow(self, profile):
        """Unfollow a profile."""
        self.following.remove(profile)

    def has_followed(self, profile):
        """Check if a user has followed the profile."""
        return self.following.filter(id=profile.id).exists()


class Profile(TimestampedModel, FollowMixin):
    """User's Profile model."""

    username = models.CharField(max_length=255, blank=True, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)

    profile_picture = models.ImageField(
        upload_to=generate_file_path, null=True, blank=True, default="defaults/zen.png"
    )

    phonenumber = PhoneNumberField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    bio = models.TextField(blank=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )

    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )

    # TODO implement Poto model for user to upload photos

    def __str__(self) -> str:
        """Return string Profile of the user: <user-email>."""
        return f"Profile of the user: {self.user.email}"

    def save(self, *args, **kwargs):
        """Save user's email as username as default."""
        if not self.username:
            self.username = self.user.email
        return super().save(*args, **kwargs)
