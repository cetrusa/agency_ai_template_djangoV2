"""Django settings for the base dashboard template.

Principios:
- Server-Driven UI (Templates) + HTMX
- Sin Node.js / sin bundlers / sin SPA
- Static assets simples (CSS tokens + CSS modular + JS mínimo)

Nota: este archivo es deliberadamente "monolítico" para facilitar clonación.
Si en el futuro se desea, puede dividirse en settings/base.py, settings/dev.py, etc.
"""

from __future__ import annotations

import os
import secrets
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Permite cargar variables desde PROJECT_BASE/.env aunque el cwd sea distinto.
load_dotenv(dotenv_path=BASE_DIR / ".env", override=False)


def _env_bool(name: str, default: bool = False) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    raw = raw.strip().lower()
    return raw in {"1", "true", "yes", "y", "on"}


def _env_list(name: str, default: list[str] | None = None) -> list[str]:
    raw = os.getenv(name)
    if raw is None:
        return list(default or [])
    return [v.strip() for v in raw.split(",") if v.strip()]


DEBUG = _env_bool("DJANGO_DEBUG", default=False)

# En DEBUG se permite generar un SECRET_KEY efímero para facilitar onboarding.
# En producción (DEBUG=False), el SECRET_KEY debe estar definido y no puede ser un placeholder.
SECRET_KEY = (os.getenv("DJANGO_SECRET_KEY") or "").strip()
if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = secrets.token_urlsafe(48)
    else:
        raise RuntimeError("DJANGO_SECRET_KEY es obligatorio cuando DJANGO_DEBUG=False")
if SECRET_KEY.lower() in {"change_me", "changeme", "django-insecure-change-me"}:
    if DEBUG:
        # En dev se tolera, pero NO debe usarse en producción.
        pass
    else:
        raise RuntimeError("DJANGO_SECRET_KEY no puede ser un placeholder cuando DJANGO_DEBUG=False")

# Nunca usar '*' por defecto. En DEBUG, permitir localhost/127.0.0.1.
ALLOWED_HOSTS = _env_list(
    "DJANGO_ALLOWED_HOSTS",
    default=["localhost", "127.0.0.1"] if DEBUG else [],
)


INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # 1st party apps
    "apps.core.apps.CoreConfig",
    "apps.core.navigation",
    "apps.accounts",
    "apps.dashboard",
    "apps.orgs",
    "apps.organization_admin",
    "apps.users_admin",
    "apps.crud_example",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.core.middleware.SetupMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # Templates reutilizables a nivel proyecto (no por app).
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.navigation.context_processors.navigation_context",
                "apps.core.context_processors.global_config_context",
            ],
        },
    }
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"


# Database: SQLite por defecto para facilitar setup inicial estilo WordPress/Moodle
# En producción o para proyectos avanzados, configura PostgreSQL/MySQL via .env
DATABASES = {
    "default": {
        "ENGINE": os.getenv("DJANGO_DB_ENGINE", "django.db.backends.sqlite3"),
        "NAME": os.getenv("DJANGO_DB_NAME", str(BASE_DIR / "db.sqlite3")),
        "USER": os.getenv("DJANGO_DB_USER", ""),
        "PASSWORD": os.getenv("DJANGO_DB_PASSWORD", ""),
        "HOST": os.getenv("DJANGO_DB_HOST", ""),
        "PORT": os.getenv("DJANGO_DB_PORT", ""),
    }
}

# Validación solo si usas PostgreSQL/MySQL explícitamente (no SQLite)
if not DEBUG and DATABASES["default"]["ENGINE"] != "django.db.backends.sqlite3":
    missing = []
    if not DATABASES["default"]["NAME"]:
        missing.append("POSTGRES_DB (o DJANGO_DB_NAME)")
    if not DATABASES["default"]["USER"]:
        missing.append("POSTGRES_USER (o DJANGO_DB_USER)")
    if not DATABASES["default"]["PASSWORD"]:
        missing.append("POSTGRES_PASSWORD (o DJANGO_DB_PASSWORD)")
    if missing:
        raise RuntimeError("Faltan variables de BD en producción: " + ", ".join(missing))


AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Baseline recomendada: longitud mínima 12.
for v in AUTH_PASSWORD_VALIDATORS:
    if v.get("NAME") == "django.contrib.auth.password_validation.MinimumLengthValidator":
        v.setdefault("OPTIONS", {})
        v["OPTIONS"].setdefault("min_length", 12)

LANGUAGE_CODE = "es"
TIME_ZONE = os.getenv("DJANGO_TIME_ZONE", "UTC")
USE_I18N = True
USE_TZ = True


STATIC_URL = "/static/"
# En modo plantilla/desarrollo: los assets viven en /static.
STATICFILES_DIRS = [BASE_DIR / "static"]
# En producción (o dentro del contenedor) se puede ejecutar collectstatic.
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# Seguridad mínima para plantilla; endurecer en proyectos reales.
CSRF_TRUSTED_ORIGINS = _env_list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[])

# Seguridad: defaults razonables (especialmente relevantes para HTMX + sesiones)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = os.getenv("DJANGO_SESSION_COOKIE_SAMESITE", "Lax")
CSRF_COOKIE_SAMESITE = os.getenv("DJANGO_CSRF_COOKIE_SAMESITE", "Lax")

if not DEBUG:
    SECURE_SSL_REDIRECT = _env_bool("DJANGO_SECURE_SSL_REDIRECT", default=True)
    SESSION_COOKIE_SECURE = _env_bool("DJANGO_SESSION_COOKIE_SECURE", default=True)
    CSRF_COOKIE_SECURE = _env_bool("DJANGO_CSRF_COOKIE_SECURE", default=True)
    SECURE_HSTS_SECONDS = int(os.getenv("DJANGO_SECURE_HSTS_SECONDS", "31536000"))
    SECURE_HSTS_INCLUDE_SUBDOMAINS = _env_bool("DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
    SECURE_HSTS_PRELOAD = _env_bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = os.getenv("DJANGO_SECURE_REFERRER_POLICY", "same-origin")
    X_FRAME_OPTIONS = os.getenv("DJANGO_X_FRAME_OPTIONS", "DENY")

    # Si estás detrás de un proxy (nginx/traefik), habilita esto.
    if _env_bool("DJANGO_BEHIND_PROXY", default=False):
        SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# RQ (infraestructura opcional: solo se usa si habilitas Redis y worker)
RQ_QUEUES = {
    "default": {
        "URL": os.getenv("REDIS_URL", "redis://redis:6379/0"),
        "DEFAULT_TIMEOUT": int(os.getenv("RQ_DEFAULT_TIMEOUT", "300")),
    },
}

# Convención de jobs: definir funciones en apps/<module>/jobs.py.
# El servidor web no debe ejecutar tareas largas; usar worker RQ cuando aplique.

# --- Authentication ---
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
