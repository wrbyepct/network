"""Custom Base model."""

from uuid import uuid4

from django.db import models


class TimestampedModel(models.Model):
    """Custom Base timstamped model with uuid and pkid for internal use."""

    pkid = models.BigAutoField(primary_key=True, editable=False)
    id = models.UUIDField(default=uuid4, unique=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ["-created_at", "-updated_at"]
