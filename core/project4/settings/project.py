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
SITE_ID = 1

ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_UNIQUE_EMAIL = True

ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
ACCOUNT_EMAIL_VERIFICATION = "none"  # Can later change to "optional" or "mandatory"

ACCOUNT_SIGNUP_FORM_CLASS = "network.user.forms.SignupForm"


SOCIALACCOUNT_LOGIN_ON_GET = True
SOCIALACCOUNT_ADAPTER = "network.user.adapters.CustomAccountAdapter"
SOCIALACCOUNT_EMAIL_AUTHENTICATION_AUTO_CONNECT = True
SOCIALACCOUNT_EMAIL_AUTHENTICATION = True

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": env("OAUTH_GOOGLE_CLIENT_ID"),
            "secret": env("OAUTH_GOOGLE_SECRET"),
        },
    },
    "twitter": {
        "APP": {
            "client_id": env("OAUTH_TIWTTER_CLIENT_ID"),
            "secret": env("OAUTH_TIWTTER_SECRET"),
        }
    },
    "facebook": {
        "APP": {
            "client_id": env("OAUTH_FACEBOOK_CLIENT_ID"),
            "secret": env("OAUTH_FACEBOOK_SECRET"),
        }
    },
}
