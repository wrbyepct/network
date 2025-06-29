# Generated by Django 5.2.1 on 2025-06-18 09:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("posts", "0009_populate_post_media_profile"),
        ("profiles", "0003_alter_profile_followers"),
    ]

    operations = [
        migrations.AlterField(
            model_name="postmedia",
            name="profile",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="medias",
                to="profiles.profile",
            ),
        ),
    ]
