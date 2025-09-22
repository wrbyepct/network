"""Custom template tags for post template."""

from django import template
from django.utils.timesince import timesince

from network.posts.services import IncubationService
from network.posts.utils import get_like_stat

register = template.Library()


@register.filter
def like_stat_str(like_count, liked):
    """Return dynamic like stat string."""
    return get_like_stat(like_count, liked)


@register.filter
def timesince_simple(value):
    """Return fisrt part of timesince."""
    result = timesince(value)

    return result.split(",")[0]


@register.filter
def get_incubating_egg_url(request):
    """Return current incubating egg url in cache if exists, else return empty string."""
    user_id = request.user.id
    return IncubationService.get_incubating_egg_url(user_id) or ""
