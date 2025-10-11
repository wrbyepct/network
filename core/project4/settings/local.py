"""Settings: local."""
# ruff: noqa: F821

# ruff: noqa: S105

import socket

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

# CaccheOPs
CACHEOPS_REDIS = "redis://redis:6379/1"
CACHEOPS_ENABLED = True
CACHEOPS_DEFAULTS = {"timeout": 60 * 60}
CACHEOPS = {
    "profiles.egg": {"ops": "all", "timeout": 60 * 60},  # 1h TTL
    "profiles.profile": {"ops": "all", "timeout": 60 * 60},  # 1h TTL
    "posts.post": {"ops": "all", "timeout": 60 * 60},
    # "profiles.profile_followers": {"ops": "all", "timeout": 60 * 60},  # 1h TTL
    # "albums.album": {"ops": "all", "timeout": 60 * 60},  # 1h TTL
    "network.user": {"ops": "all", "timeout": 60 * 60},  # 1h TTL
}


# DEV TOOLBAR
DEBUG_TOOLBAR_CONFIG = {
    "SHOW_TOOLBAR_CALLBACK": lambda _: True,  # always show
}

INTERNAL_IPS = ["127.0.0.1"]
try:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [
        ip.rsplit(".", 1)[0] + ".1" for ip in ips
    ]  # gateway .1 on docker bridge
except Exception:  # noqa: BLE001, S110
    pass


# Email backend for password reset
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER
