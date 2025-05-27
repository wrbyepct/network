"""Settings: Base."""

# ruff: noqa: F821
STATIC_URL = "/static/"

MEDIA_URL = "/media/"
MEDIA_ROOT = str(BASE_DIR / "network" / "media")


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",  # default for admin
    "allauth.account.auth_backends.AuthenticationBackend",  # allows allauth to handle logins
]


AUTH_USER_MODEL = "network.User"

# allauth
ACCOUNT_EMAIL_VERIFICATION = None


# login logout

LOGIN_REDIRECT_URL = "/"  # After login, where to go
ACCOUNT_LOGOUT_REDIRECT_URL = "/accounts/login/"  # After logout


# Require email? Optional. For now, no email verification
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"  # Can later change to "optional" or "mandatory"

ACCOUNT_SIGNUP_FORM_CLASS = "network.user.forms.SignupForm"


GOOGLE_PROVIDER_CLIENT_ID = env("GOOGLE_PROVIDER_CLIENT_ID")
GOOGLE_PROVIDER_SECRET = env("GOOGLE_PROVIDER_SECRET")

SITE_ID = 1

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": GOOGLE_PROVIDER_CLIENT_ID,
            "secret": GOOGLE_PROVIDER_SECRET,
            "key": "",
        },
    },
}

SOCIALACCOUNT_LOGIN_ON_GET = True
