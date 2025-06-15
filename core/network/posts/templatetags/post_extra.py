"""Custom template tags for post template."""

from django import template

register = template.Library()


@register.filter
def liked_by_user(post, user):
    """Check if a post is liked by a user."""
    if not user.is_authenticated:
        return False
    return post.likes.filter(user=user).exists()
