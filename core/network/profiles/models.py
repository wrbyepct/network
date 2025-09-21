"""Profile models."""

from django.conf import settings
from django.core.exceptions import BadRequest
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField

from network.common.models import TimestampedModel
from network.tools.media import generate_file_path

from .services import ActivityManagerService


class FollowMixin:
    """Functions for follow and unflow a profile."""

    def follow(self, profile):
        """Follow a profile."""
        if profile.id == self.id:
            message = "You cannot follow yourself."
            raise BadRequest(message)

        self.following.add(profile)

    def unfollow(self, profile):
        """Unfollow a profile."""
        self.following.remove(profile)

    def has_followed(self, profile):
        """Check if a user has followed the profile."""
        return self.following.filter(id=profile.id).exists()


class Profile(TimestampedModel, FollowMixin):
    """User's Profile model."""

    username = models.CharField(max_length=255, blank=True, unique=True)
    first_name = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=255, blank=True)

    profile_picture = models.ImageField(
        upload_to=generate_file_path, null=True, blank=True, default="defaults/zen.png"
    )

    phonenumber = PhoneNumberField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    bio = models.TextField(blank=True)

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile"
    )

    followers = models.ManyToManyField(
        "self", symmetrical=False, related_name="following", blank=True
    )

    def __str__(self) -> str:
        """Return string Profile of the user: <user-email>."""
        return f"Profile of the user: {self.user.email}"

    def save(self, *args, **kwargs):
        """Save user's email as username as default."""
        if not self.username:
            self.username = self.user.email
        return super().save(*args, **kwargs)

    @property
    def albums_count(self):
        """Return profile's albums count."""
        return self.albums.count()

    @property
    def special_eggs(self):
        """Return user's speical eggs."""
        return Egg.objects.filter(egg_type="special", user=self.user)

    @property
    def regular_eggs(self):
        """Return user's regular eggs."""
        return Egg.objects.filter(egg_type="regular", user=self.user)

    @property
    def easter_eggs(self):
        """Return user's easter eggs."""
        return Egg.objects.filter(egg_type="easter", user=self.user)

    @property
    def total_eggs_count(self):
        """Return total eggs count."""
        return (
            self.easter_eggs.count()
            + self.special_eggs.count()
            + self.regular_eggs.count()
        )

    @property
    def posts(self):
        """Return user's posts count."""
        return self.user.posts.all()

    @property
    def activity(self):
        """Return user's actiity status."""
        return ActivityManagerService.get_activity_obj(user=self.user)


class SpecialEggChoices(models.TextChoices):
    """Special egg choices."""

    VOLCANO = "volcano", "Volcano"
    RAINBOW = "rainbow", "Rainbow"
    DEVIL = "devil", "Devil"
    ANGEL = "angel", "Angel"
    SKULL = "skull", "Skull"
    SWAMP = "swamp", "Swamp"
    GOLDEN = "golden", "Golden"
    SILVER = "silver", "Silver"
    THUNDER = "thunder", "Thunder"
    BUBBLE = "bubble", "Bubble"
    LUCKY = "lucky", "Lucky"
    CANDY = "candy", "Candy"
    STAR = "star", "Star"
    SAKURA = "sakura", "Sakura"
    CYBER = "cyber", "Cyber"
    UNIVERSE = "universe", "Universe"
    RUBIKS_CUBE = "rubik's cube", "Rubik's Cube"


class RegularEggChoices(models.TextChoices):
    """Regular egg choices."""

    TEAL = "teal", "Teal"
    ORANGE = "orange", "Orange"
    YELLOW = "yellow", "Yellow"
    RED = "red", "Red"
    GREEN = "green", "Green"
    BLUE = "blue", "Blue"
    PURPLE = "purple", "Purple"
    Chicken = "chiken", "Chicken"


class EasterEggChoices(models.TextChoices):
    """Regular egg choices."""

    GLICHY = "glichy", "Glichy"
    BUGGY = "buggy", "Buggy"
    EASTER = "easter", "Easter"


class EggTypeChoices(models.TextChoices):
    """Egg type."""

    SPECIAL = "special", "Special"
    REGULAR = "regular", "Regular"
    EASTER = "easter", "Easter"


class Egg(TimestampedModel):
    """Egg model."""

    url = models.CharField(max_length=255)
    quantity = models.PositiveSmallIntegerField(default=1)
    name = models.CharField(max_length=20)
    egg_type = models.CharField(max_length=20, choices=EggTypeChoices)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="eggs"
    )

    def save(self, *args, **kwargs):
        """Override to also save egg url."""
        from network.posts.services import EggManageService

        self.name = EggManageService.get_egg_name(self.url)

        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """Return egg info."""
        return f"{self.egg_type} egg: {self.name}"
