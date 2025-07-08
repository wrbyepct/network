"""Profile admin."""

from django.contrib import admin

from .models import Post, PostMedia


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Custome Post admin."""

    list_display = ["id", "username"]
    list_display_links = ["id"]

    def username(self, obj):
        """Get username."""
        return obj.user.profile.username


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    """Custome PostMeida admin."""

    list_filter = ["profile"]
