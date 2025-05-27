"""Create default admin user command."""

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from network.user.constants import ADMIN_EMAIL, ADMIN_PASSWORD


class Command(BaseCommand):
    """Command for creating default admin user."""

    def handle(self, *args, **options):
        """Create a default admin user."""
        User = get_user_model()  # noqa: N806

        admin_user = User.objects.filter(email=ADMIN_EMAIL).exists()

        if not admin_user:
            User.objects.create_superuser(email=ADMIN_EMAIL, password=ADMIN_PASSWORD)
            self.stdout.write(self.style.SUCCESS("Superuser created."))
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"Admin user with this email {ADMIN_EMAIL} already exists."
                )
            )
