"""Custom validators."""

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


validate_image_extension = partial(
    _validate_extension, allowed_exts=ALLOWED_POST_IMAGE_EXT
)
validate_video_extension = partial(
    _validate_extension, allowed_exts=ALLOWED_POST_VIDEO_EXT
)


validate_media_extension = partial(
    _validate_extension, allowed_exts=(ALLOWED_POST_VIDEO_EXT + ALLOWED_POST_IMAGE_EXT)
)
