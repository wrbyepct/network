"""Custom profile template filter."""

import random

from django import template

register = template.Library()


@register.filter
def has_followed(profile, user):
    """Check if the user has followed the profile."""
    if not user.is_authenticated:
        return False
    user_profile = user.profile
    return user_profile.has_followed(profile)


@register.filter
def random_egg(eggs):
    """Return user's random speical egg."""
    return random.choice(eggs)
