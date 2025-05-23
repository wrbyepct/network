"""Create default admin user command."""

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from network.user.constants import ADMIN_PASSWORD, ADMIN_USERNAME


class Command(BaseCommand):
    """Command for creating default admin user."""

    def handle(self, *args, **options):
        """Create a default admin user."""
        User = get_user_model()  # noqa: N806

        admin_user = User.objects.filter(username=ADMIN_USERNAME).exists()

        if not admin_user:
            User.objects.create_superuser(
                username=ADMIN_USERNAME, password=ADMIN_PASSWORD
            )
            self.stdout.write(self.style.SUCCESS("Superuser created."))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin user with this username {ADMIN_USERNAME} already exists."
                )
            )
