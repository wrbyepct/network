"""Command for creating social account apps."""

from allauth.socialaccount.models import SocialApp
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Create a SocialApp for the current site."""

    help = "Create a SocialApp for the current site"

    def handle(self, *args, **options):
        """Create Site with correct domain and link it to SocialApp."""
        config = getattr(settings, "SOCIALAPP_SEED", None)
        if not config:
            self.stderr.write("❌ Socical App SEED for creating Social App not found.")
            return

        # create site
        site, _ = Site.objects.get_or_create(domain=config["site_domain"])
        site.name = config["site_name"]
        site.save()
        self.stdout.write(f"✅ Site set to: {site.domain}")

        # create app
        for provider in config["providers"]:
            app, created = SocialApp.objects.get_or_create(
                provider=provider["provider"],
                defaults={
                    "client_id": provider["client_id"],
                    "secret": provider["secret"],
                    "name": provider["name"],
                },
            )
            if not created:
                self.stdout.write(f"Social App already exists: {app.name}")

            else:
                self.stdout.write(f"✅ Created SocialApp: {app.name}")

            # add site to app
            app.sites.add(site)
            app.save()

            self.stdout.write(
                f"🎉 SocialApp: {app.name} linked to site {site.domain} and ready to use."
            )
