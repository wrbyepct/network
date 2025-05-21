"""Wait for db response command."""

import time

from django.core.management import BaseCommand
from django.db import connections
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2OpError


class Command(BaseCommand):
    """Command to wait for DB connection."""

    def handle(self, *args, **options):
        """Wait for postgres db."""
        self.stdout.write("Waiting for PostgreSQL to become available...")
        suggest_unrecoverable_after = 30
        start = time.time()
        while True:
            try:
                conn = connections["default"]
                conn.cursor()
                break
            except (Psycopg2OpError, OperationalError) as e:
                self.stdout.write("Waiting for PostgreSQL to become available...\n")
                if time.time() - start > suggest_unrecoverable_after:
                    self.stderr.write(
                        f"This is taking longer than expected, the following exception may be indicative of an unrecoverable error: '{e}'\n"
                    )
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS("PostgreSQL is available."))
