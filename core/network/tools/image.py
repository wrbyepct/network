"""Tools for processing image."""

from pathlib import Path
from uuid import uuid4


def generate_file_path(instance, filename):  # noqa: ARG001
    """
    Change uploaded image file name to uuid4 string + extension.

    For example: uploads/<app_name>/<uuid4>.jpg
    """
    path = Path(filename)
    ext = path.suffix

    return Path("uploads") / f"{uuid4()}{ext}"
