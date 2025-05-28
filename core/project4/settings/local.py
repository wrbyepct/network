"""Settings: local."""
# ruff: noqa: F821

# ruff: noqa: S105
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost"]
