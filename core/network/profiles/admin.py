"""Profile admin."""

from django.contrib import admin

from .models import Egg, Profile


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Custom Profile admin."""


@admin.register(Egg)
class EggAdmin(admin.ModelAdmin):
    """Custom Profile admin."""
