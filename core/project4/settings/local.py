"""Settings: local."""
# ruff: noqa: F821

# ruff: noqa: S105
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost"]

# Redi cache.
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/0",
    }
}

# Celery settings
CELERY_BROKER_URL = "redis://redis:6379/0"
# TODO figure out why this is set to None
CELERY_RESULT_BACKEND = None
