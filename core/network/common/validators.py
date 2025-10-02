"""Custom validators."""

import json
from functools import partial

from django.core.exceptions import ValidationError

from .constants import ALLOWED_POST_IMAGE_EXT, ALLOWED_POST_VIDEO_EXT


def _validate_extension(file, allowed_exts=None):
    """Validate uploaded image is of correct extension."""
    try:
        _, ext = file.name.rsplit(".", 1)
        if ext.lower() not in allowed_exts:
            msg = f"File: '{file.name}' is not in allowed types: {allowed_exts}"
            raise ValidationError(msg)  # noqa: TRY301
        return file  # noqa: TRY300
    except Exception as e:  # noqa: BLE001
        raise ValidationError(e)  # noqa: B904


def validate_image_extension(ext_str):
    """Valiate images extension."""
    image_exts = json.loads(ext_str)

    for ext in image_exts:
        if ext not in ALLOWED_POST_IMAGE_EXT:
            msg = f"Uploaded image is not in allowed types: {ALLOWED_POST_IMAGE_EXT}"
            raise ValidationError(msg)


def validate_video_extension(ext_str):
    """Validate video extension."""
    video_exts = json.loads(ext_str)

    for ext in video_exts:
        if ext not in ALLOWED_POST_VIDEO_EXT:
            msg = f"Uploaded video is not in allowed types: {ALLOWED_POST_IMAGE_EXT}"
            raise ValidationError(msg)


validate_media_extension = partial(
    _validate_extension, allowed_exts=(ALLOWED_POST_VIDEO_EXT + ALLOWED_POST_IMAGE_EXT)
)  # used by album media upload
