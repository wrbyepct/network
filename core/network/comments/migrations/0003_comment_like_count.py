# Generated by Django 5.2.1 on 2025-06-28 07:51

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("comments", "0002_commentlike"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment",
            name="like_count",
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
