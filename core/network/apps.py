"""App."""

from django.apps import AppConfig


class NetworkConfig(AppConfig):
    name = "network"

    def ready(self):
        from network import signals  # noqa: F401
