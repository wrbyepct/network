"""Custom template tags for post template."""

from django import template
from django.utils.timesince import timesince

from network.posts.utils import get_like_stat

register = template.Library()


@register.filter
def liked_by_user(obj, user):
    """Check if the instance is liked by a user."""
    if not user.is_authenticated:
        return False
    return obj.likes.filter(user=user).exists()


@register.filter
def like_stat_str(like_count, liked):
    """Return dynamic like stat string."""
    return get_like_stat(like_count, liked)


@register.filter
def timesince_simple(value):
    """Return fisrt part of timesince."""
    result = timesince(value)

    return result.split(",")[0]
