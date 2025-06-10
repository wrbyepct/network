"""Profile admin."""

from django.contrib import admin

from .models import Post, PostMedia


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Custome Post admin."""


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    """Custome PostMeida admin."""
