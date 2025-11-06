"""Profile admin."""

from django.contrib import admin

from .models import Post, PostMedia


class PostMediaInline(admin.TabularInline):  # or StackedInline
    """Post Medias Inline."""

    model = PostMedia
    extra = 1  # how many empty forms to show
    min_num = 0  # minimum number of related objects


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Custome Post admin."""

    list_display = ["id", "username", "content"]
    list_display_links = ["id"]
    ordering = ["-created_at"]
    inlines = [PostMediaInline]

    def username(self, obj):
        """Get username."""
        return obj.user.profile.username


@admin.register(PostMedia)
class PostMediaAdmin(admin.ModelAdmin):
    """Custome PostMeida admin."""

    list_filter = ["profile"]
    list_display = ["id"]
    search_fields = ["id"]
    ordering = ["created_at"]
