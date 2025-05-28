"""Logging."""

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,  # Keeps the default Django loggers active
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {
            "format": "[{levelname}] {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",  # You can also use 'verbose'
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "WARNING",  # Change to 'DEBUG' to see more logs
    },
    "loggers": {
        "allauth": {
            "handlers": ["console"],
            "level": "DEBUG",
        },
        "django": {
            "handlers": ["console"],
            "level": "INFO",  # Use DEBUG for development
            "propagate": False,
        },
    },
}
