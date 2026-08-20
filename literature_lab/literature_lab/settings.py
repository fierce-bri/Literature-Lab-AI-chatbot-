"""Django settings for the Literature Lab project."""

from __future__ import annotations

import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def _environment_boolean(
    name: str,
    default: bool,
) -> bool:
    """Read a boolean environment variable."""

    default_value = (
        "true"
        if default
        else "false"
    )

    return os.getenv(
        name,
        default_value,
    ).strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _environment_list(
    name: str,
    default: str = "",
) -> list[str]:
    """Read a comma-separated environment variable."""

    return [
        value.strip()
        for value in os.getenv(
            name,
            default,
        ).split(",")
        if value.strip()
    ]


DEBUG = _environment_boolean(
    "DJANGO_DEBUG",
    True,
)


SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY"
)

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = (
            "django-insecure-development-only-change-me"
        )
    else:
        raise RuntimeError(
            "DJANGO_SECRET_KEY must be set "
            "when DJANGO_DEBUG is false."
        )


ALLOWED_HOSTS = _environment_list(
    "DJANGO_ALLOWED_HOSTS",
    "127.0.0.1,localhost",
)


CSRF_TRUSTED_ORIGINS = _environment_list(
    "DJANGO_CSRF_TRUSTED_ORIGINS"
)


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "chatbot",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


ROOT_URLCONF = "literature_lab.urls"


TEMPLATES = [
    {
        "BACKEND": (
            "django.template.backends."
            "django.DjangoTemplates"
        ),
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                (
                    "django.template.context_processors."
                    "debug"
                ),
                (
                    "django.template.context_processors."
                    "request"
                ),
                (
                    "django.contrib.auth."
                    "context_processors.auth"
                ),
                (
                    "django.contrib.messages."
                    "context_processors.messages"
                ),
            ],
        },
    },
]


WSGI_APPLICATION = (
    "literature_lab.wsgi.application"
)


DATABASE_PATH = Path(
    os.getenv(
        "DJANGO_DATABASE_PATH",
        str(
            BASE_DIR
            / "db.sqlite3"
        ),
    )
)


DATABASES = {
    "default": {
        "ENGINE": (
            "django.db.backends.sqlite3"
        ),
        "NAME": DATABASE_PATH,
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "UserAttributeSimilarityValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "MinimumLengthValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "CommonPasswordValidator"
        ),
    },
    {
        "NAME": (
            "django.contrib.auth."
            "password_validation."
            "NumericPasswordValidator"
        ),
    },
]


LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


STATIC_URL = "/static/"

STATIC_ROOT = (
    BASE_DIR
    / "staticfiles"
)


STORAGES = {
    "default": {
        "BACKEND": (
            "django.core.files.storage."
            "FileSystemStorage"
        ),
    },
    "staticfiles": {
        "BACKEND": (
            "whitenoise.storage."
            "CompressedManifestStaticFilesStorage"
        ),
    },
}


DEFAULT_AUTO_FIELD = (
    "django.db.models.BigAutoField"
)
