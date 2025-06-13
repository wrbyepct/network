# Generated by Django 5.2.1 on 2025-06-01 09:20

import uuid

import django.db.models.deletion
import phonenumber_field.modelfields
from django.conf import settings
from django.db import migrations, models

import network.profiles.models
import network.tools.media


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Profile",
            fields=[
                (
                    "pkid",
                    models.BigAutoField(
                        editable=False, primary_key=True, serialize=False
                    ),
                ),
                (
                    "id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("username", models.CharField(blank=True, max_length=255)),
                ("first_name", models.CharField(blank=True, max_length=255)),
                ("last_name", models.CharField(blank=True, max_length=255)),
                (
                    "profile_picture",
                    models.ImageField(
                        blank=True,
                        default="defaults/zen.png",
                        null=True,
                        upload_to=network.tools.media.generate_file_path,
                    ),
                ),
                (
                    "phonenumber",
                    phonenumber_field.modelfields.PhoneNumberField(
                        blank=True, max_length=128, region=None
                    ),
                ),
                ("birth_date", models.DateField(blank=True, null=True)),
                ("bio", models.TextField(blank=True)),
                (
                    "followers",
                    models.ManyToManyField(
                        related_name="following", to="profiles.profile"
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="profile",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "ordering": ["-created_at", "-updated_at"],
                "abstract": False,
            },
            bases=(models.Model, network.profiles.models.FollowMixin),
        ),
    ]
