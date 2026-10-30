import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


def _load_env_file():
    path = BASE_DIR / ".env"
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


_load_env_file()

SECRET_KEY = os.environ.get(
    "OKIA_SECRET_KEY",
    "dev-only-okia-secret-change-before-any-shared-use",
)
DEBUG = os.environ.get("OKIA_ENV", "back") != "production"
ALLOWED_HOSTS = [
    host
    for host in os.environ.get("OKIA_ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.accounts",
    "apps.access",
    "apps.erp",
    "apps.margins",
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
WSGI_APPLICATION = "config.wsgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    }
]

def _sqlite():
    return {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }


def _mssql(prefix):
    return {
        "ENGINE": "mssql",
        "NAME": os.environ[f"{prefix}_NAME"],
        "USER": os.environ.get(f"{prefix}_USER", ""),
        "PASSWORD": os.environ.get(f"{prefix}_PASSWORD", ""),
        "HOST": os.environ.get(f"{prefix}_HOST", "localhost"),
        "PORT": os.environ.get(f"{prefix}_PORT", "1433"),
        "OPTIONS": {
            "driver": os.environ.get(
                f"{prefix}_ODBC_DRIVER",
                "ODBC Driver 18 for SQL Server",
            ),
            "extra_params": "TrustServerCertificate=yes",
        },
    }


def _default_database():
    if os.environ.get("OKIA_ENV") == "production":
        return _mssql("APP")
    return _sqlite()


DATABASES = {"default": _default_database()}
DATABASE_ROUTERS = ["apps.erp.router.ErpRouter"]

# El origen comercial se lee con pyodbc. El backend Django de SQL Server no está instalado.
ERP_NAME = os.environ.get("ERP_NAME", "")

if "pytest" in sys.modules or os.environ.get("OKIA_SAMPLE") == "1":
    SAMPLE_ERP = True
elif ERP_NAME:
    SAMPLE_ERP = False
else:
    SAMPLE_ERP = os.environ.get("OKIA_SAMPLE") != "0"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "es"
TIME_ZONE = "Europe/Madrid"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = "login"
LOGIN_REDIRECT_URL = "company-select"
LOGOUT_REDIRECT_URL = "login"

SESSION_COOKIE_AGE = 60 * 60 * 24 * 30
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
PASSWORD_RESET_TIMEOUT = 60 * 60
EMAIL_BACKEND = os.environ.get(
    "OKIA_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}
