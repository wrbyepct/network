"""Profile admin."""

from django.contrib import admin

from .models import Post


@admin.register(Post)
class ProfileAdmin(admin.ModelAdmin):
    """Custome Post admin."""
