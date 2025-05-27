"""Settings: local."""
# ruff: noqa: F821

# ruff: noqa: S105
SECRET_KEY = env("DJANGO_SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["localhost"]

SOCIALAPP_SEED = {
    "providers": [
        {
            "provider": "google",
            "client_id": GOOGLE_PROVIDER_CLIENT_ID,
            "secret": GOOGLE_PROVIDER_SECRET,
            "name": "Google Local Dev",
        },
    ],
    "site_domain": env("DOMAIN"),  # <- must match what you're running in dev
    "site_name": env("SITE_NAME"),
}
