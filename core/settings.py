from os import getenv
from pathlib import Path
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / '.env')

SECRET_KEY = getenv('SECRET_KEY')

DEBUG = getenv('DEBUG', False)

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Third-party apps
    'corsheaders',
    'ninja_extra',
    'ninja_jwt.token_blacklist',
    # Local apps
    'users',
    'organizations'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'core.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'core.wsgi.application'

if not DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': getenv('PGDATABASE'),
            'USER': getenv('PGUSER'),
            'PASSWORD': getenv('PGPASSWORD'),
            'HOST': getenv('PGHOST'),
            'PORT': getenv('PGPORT', 5432),
            'OPTIONS': {
            'sslmode': 'require',
            },
        }
    }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': getenv('DEVPGDATABASE'),
        'USER': getenv('DEVPGUSER'),
        'PASSWORD': getenv('DEVPGPASSWORD'),
        'HOST': getenv('DEVPGHOST'),
        'PORT': getenv('DEVPGPORT', 5432),
        'OPTIONS': {
        'sslmode': 'require',
        },
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True

STATIC_URL = 'static/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

AUTH_USER_MODEL = 'users.User'

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

CORS_ALLOWED_ORIGINS = [
    "https://example.com",
    "https://sub.example.com",
    "http://localhost:8080",
    "http://127.0.0.1:9000",
]

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# EMAIL_HOST = getenv('EMAIL_HOST', default=None)

# EMAIL_PORT = getenv('EMAIL_PORT', default='587') # Recommended

# EMAIL_HOST_USER = getenv('EMAIL_HOST_USER', default=None)

# EMAIL_HOST_PASSWORD = getenv('EMAIL_HOST_PASSWORD', default=None)

# EMAIL_USE_TLS = getenv('EMAIL_USE_TLS', default=True)  # Use EMAIL_PORT 587 for TLS

# # EMAIL_USE_SSL = getenv('EMAIL_USE_TLS', default=False)  # EUse MAIL_PORT 465 for SSL

# ADMIN_USER_NAME=getenv('ADMIN_USER_NAME', default='Admin user')

# ADMIN_USER_EMAIL=getenv('ADMIN_USER_EMAIL', default=None)

# MANAGERS=[]
# ADMINS=[]
# if all([ADMIN_USER_NAME, ADMIN_USER_EMAIL]):
#     ADMINS +=[
#         (f'{ADMIN_USER_NAME}', f'{ADMIN_USER_EMAIL}')
#     ]
#     MANAGERS=ADMINS

NINJA_JWT = {
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': False,
    # 'SIGNING_KEY': getenv('SECRET_KEY'),
}
