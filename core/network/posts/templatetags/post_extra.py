"""Custom template tags for post template."""

from django import template
from django.utils.timesince import timesince

register = template.Library()


@register.filter
def liked_by_user(obj, user):
    """Check if the instance is liked by a user."""
    if not user.is_authenticated:
        return False
    return obj.likes.filter(user=user).exists()


@register.filter
def timesince_simple(value):
    """Return fisrt part of timesince."""
    result = timesince(value)

    return result.split(",")[0]
