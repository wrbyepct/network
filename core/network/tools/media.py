"""Tools for processing image."""

from functools import partial
from pathlib import Path
from uuid import uuid4


def generate_file_path(instance, filename, path_prefix="uploads"):  # noqa: ARG001
    """
    Change uploaded image file name to uuid4 string + extension.

    For example: uploads/<app_name>/<uuid4>.jpg
    """
    path = Path(filename)
    ext = path.suffix

    return Path(path_prefix) / f"{uuid4()}{ext}"


post_media_path = partial(generate_file_path, path_prefix="posts")
