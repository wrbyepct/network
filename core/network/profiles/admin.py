"""Profile admin."""

from django.contrib import admin

from .models import Profile, RegularEgg, SpecialEgg


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Custom Profile admin."""


@admin.register(SpecialEgg)
class SpecialEggAdmin(admin.ModelAdmin):
    """Custom Special Egg admin."""


@admin.register(RegularEgg)
class RegularEggAdmin(admin.ModelAdmin):
    """Custom Special Egg admin."""
