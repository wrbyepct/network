"""Custom form filter."""

from django import template

register = template.Library()


@register.filter(name="add_class")
def add_class(field, css):
    """Add classes for forms in html."""
    return field.as_widget(attrs={"class": css})
