# Generated by Django 5.2.1 on 2025-05-31 18:36

from django.db import migrations, models

import network.tools.media


class Migration(migrations.Migration):
    dependencies = [
        ("network", "0006_alter_profile_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="profile_picture",
            field=models.ImageField(
                blank=True,
                default="defaults/zen.png",
                null=True,
                upload_to=network.tools.media.generate_file_path,
            ),
        ),
    ]
