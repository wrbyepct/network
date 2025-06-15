"""Custom profile template filter."""

from django import template

register = template.Library()


@register.filter
def has_followed(profile, user):
    """Check if the user has followed the profile."""
    if not user.is_authenticated:
        return False
    user_profile = user.profile
    return user_profile.has_followed(profile)
