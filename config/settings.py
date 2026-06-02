"""Django settings for the template.

All environment-driven config flows through `env` (django-environ), which reads
`.env` and parses typed values — including `DATABASE_URL`, the single switch
between SQLite and MySQL. Don't read os.environ elsewhere; add knobs here.
"""
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# django-environ: declare types + defaults, then load .env if present.
env = environ.Env(
    DJANGO_DEBUG=(bool, False),
    DJANGO_ALLOWED_HOSTS=(list, ["127.0.0.1", "localhost"]),
)
environ.Env.read_env(BASE_DIR / ".env")

# SECURITY: the default is fine for local dev only. Set DJANGO_SECRET_KEY in .env
# (and never commit it) for anything that leaves your machine.
SECRET_KEY = env("DJANGO_SECRET_KEY", default="dev-insecure-change-me")
DEBUG = env("DJANGO_DEBUG")
ALLOWED_HOSTS = env("DJANGO_ALLOWED_HOSTS")

INSTALLED_APPS = [
    # Django's batteries — the admin (django.contrib.admin) is the big reason to
    # reach for Django over a micro-framework, so it's wired up out of the box.
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third-party: DRF for the API, drf-spectacular for OpenAPI docs.
    "rest_framework",
    "drf_spectacular",
    # Local apps.
    "catalog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

# The one switch between backends. env.db() parses DATABASE_URL into Django's
# DATABASES dict, picking the right ENGINE from the scheme:
#   SQLite: sqlite:///./django_app.db   ->  django.db.backends.sqlite3
#   MySQL:  mysql://user:pass@host/db   ->  django.db.backends.mysql  (via PyMySQL)
DATABASES = {
    "default": env.db("DATABASE_URL", default=f"sqlite:///{BASE_DIR / 'django_app.db'}"),
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# DRF: drf-spectacular generates the OpenAPI schema from the serializers + views.
# AllowAny keeps the template open for local poking; tighten for real projects.
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.AllowAny"],
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Django API Template",
    "DESCRIPTION": "Starter backend: Django + Django REST Framework + drf-spectacular.",
    "VERSION": "0.1.0",
    "SERVE_INCLUDE_SCHEMA": False,
}
