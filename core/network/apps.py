"""App."""

from django.apps import AppConfig


class NetworkConfig(AppConfig):
    name = "network"

    def ready(self):
        from core.network.user import signals  # noqa: F401
