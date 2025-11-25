from pathlib import Path
from django.core.management.utils import get_random_secret_key
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = get_random_secret_key()  # para dev; para produção use variável ambiente

DEBUG = True

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Apps do projeto
    "usuarios.apps.UsuariosConfig",
    "propriedades.apps.PropriedadesConfig",
    "reservas.apps.ReservasConfig",
    "avaliacoes.apps.AvaliacoesConfig",
    "mensagens.apps.MensagensConfig",
    # App de recomendações (contém ML, endpoints e comandos)
    "recomendacoes.apps.RecomendacoesConfig",
    "favoritos",
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

ROOT_URLCONF = "aluga_ai_web.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "mensagens.context_processors.unread_count",
            ],
        },
    }
]

WSGI_APPLICATION = "aluga_ai_web.wsgi.application"
ASGI_APPLICATION = "aluga_ai_web.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
# During development we keep the source static files in `assets/`.
# This was migrated from the top-level `static/` folder. keep STATIC_URL = '/static/'
# so the app still serves them at /static/; Django will read them from `assets/`.
STATICFILES_DIRS = [os.path.join(BASE_DIR, "assets")]

# Where collectstatic will place collected files for production / deployments
# Use a separate directory so the source `static/` (dev) and collected files
# don't conflict. Docker images and deploy steps mount this path when needed.
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGIN_URL = 'usuarios:login'
