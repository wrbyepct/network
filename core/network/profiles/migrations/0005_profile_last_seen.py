# Generated by Django 5.2.1 on 2025-07-21 07:37

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("profiles", "0004_profile_activity_status"),
    ]

    operations = [
        migrations.AddField(
            model_name="profile",
            name="last_seen",
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]
