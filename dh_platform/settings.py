import os
from pathlib import Path
from datetime import timedelta

BASE_DIR = Path(__file__).resolve().parent.parent

# .env file read karo
_env_path = BASE_DIR / '.env'
if _env_path.exists():
    with open(_env_path) as _f:
        for _line in _f:
            _line = _line.strip()
            if _line and not _line.startswith('#') and '=' in _line:
                _k, _v = _line.split('=', 1)
                os.environ.setdefault(_k.strip(), _v.strip())

def env(key, default=None):
    return os.environ.get(key, default)

def env_bool(key, default=True):
    return os.environ.get(key, str(default)).lower() in ('true', '1', 'yes')

# ── Core ──────────────────────────────────────────────────────────────────────
SECRET_KEY    = env('SECRET_KEY', 'dh-secret-key-change-in-production-2026')
DEBUG         = env_bool('DEBUG', True)
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'authentication',
    'subscriptions',
    'scores',
    'draws',
    'charities',
    'winners',
    'dashboard',
    'userpannel',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'dh_platform.urls'

TEMPLATES = [{
    'BACKEND': 'django.template.backends.django.DjangoTemplates',
    'DIRS': [BASE_DIR / 'templates'],
    'APP_DIRS': True,
    'OPTIONS': {
        'context_processors': [
            'django.template.context_processors.debug',
            'django.template.context_processors.request',
            'django.contrib.auth.context_processors.auth',
            'django.contrib.messages.context_processors.messages',
        ],
    },
}]

WSGI_APPLICATION = 'dh_platform.wsgi.application'

# ── Database (Supabase) ───────────────────────────────────────────────────────
DATABASES = {
    'default': {
        'ENGINE':   'django.db.backends.postgresql',
        'NAME':     env('DB_NAME',     'postgres'),
        'USER':     env('DB_USER',     'postgres'),
        'PASSWORD': env('DB_PASSWORD', 'postgres'),
        'HOST':     env('DB_HOST',     'localhost'),
        'PORT':     env('DB_PORT',     '5432'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

AUTH_USER_MODEL = 'authentication.User'

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME':    timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME':   timedelta(days=30),
    'ROTATE_REFRESH_TOKENS':    True,
    'BLACKLIST_AFTER_ROTATION': True,
}

CORS_ALLOW_ALL_ORIGINS = True

STATIC_URL       = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT      = BASE_DIR / 'staticfiles'

MEDIA_URL  = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LANGUAGE_CODE = 'en-gb'
TIME_ZONE     = 'Europe/London'
USE_I18N      = True
USE_TZ        = True

STRIPE_SECRET_KEY     = env('STRIPE_SECRET_KEY',     'sk_test_xxx')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', 'whsec_xxx')

MONTHLY_PRICE       = 9.99
YEARLY_PRICE        = 89.99
CHARITY_MIN_PERCENT = 10
PRIZE_POOL_PERCENT  = 40
MAX_SCORES_PER_USER = 5
SCORE_MIN           = 1
SCORE_MAX           = 45