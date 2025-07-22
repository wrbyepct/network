"""User app signals."""

import logging

from django.conf import settings
from django.contrib.auth.signals import user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.timezone import now

from network.profiles.models import Profile

logger = logging.getLogger(__name__)


def create_profile(user):
    """Create user's profile."""
    Profile.objects.create(user=user)
    logger.info(f"User {user.email}'s profile has been created. ")


@receiver(signal=post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """Create profile when user is created."""
    if created:
        create_profile(user=instance)


@receiver(user_logged_out)
def update_last_logout(sender, request, user, **kwargs):
    user.last_logout = now()
    user.save(update_fields=["last_logout"])
