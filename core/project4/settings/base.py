"""Settings: Base."""
# ruff: noqa: F821
# Application definition

MY_APPS = [
    "network",
    "network.profiles",
    "network.posts",
    "network.albums",
    "network.comments",
    "network.common",
]

BASE_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Required by allauth
]

THIRD_PARTY_APPS = [
    # Allauth core
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    # Social providers
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.twitter",
    "phonenumber_field",  # Profile
    "widget_tweaks",  # Widget tweaks
    "sass_processor",  # SCSS
    # Debug
    "django_extensions",
]

INSTALLED_APPS = BASE_APPS + MY_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    # "network.middlewares.sessionswatch.SessionWatchMiddleware", # my middileware
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Required by latest django-allauth
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "project4.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "network" / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


WSGI_APPLICATION = "project4.wsgi.application"


# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": Path(BASE_DIR) / "db.sqlite3",
    }
}


# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_L10N = True

USE_TZ = True
