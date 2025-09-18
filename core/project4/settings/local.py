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
    "profiles.Egg": {"ops": "all", "timeout": 60 * 60},  # 1h TTL
}


# DEV TOOLBAR

DEBUG_TOOLBAR_CONFIG = {}

INTERNAL_IPS = ["127.0.0.1"]
try:
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS += [
        ip.rsplit(".", 1)[0] + ".1" for ip in ips
    ]  # gateway .1 on docker bridge
except Exception:  # noqa: BLE001, S110
    pass
