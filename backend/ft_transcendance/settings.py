"""
Django settings for ft_transcendance project.

Generated by 'django-admin startproject' using Django 4.2.16.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from datetime import timedelta
import os
from dotenv import load_dotenv

load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Secret key and debug mode
SECRET_KEY = os.getenv('SECRET_KEY')  # Secret key for cryptographic signing
DEBUG = os.getenv('DEBUG') == 'True'  # Should be False in production
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',') # Allowed hosts for deployment

# Installed apps
INSTALLED_APPS = [
    'django.contrib.admin',  # Admin panel
    'django.contrib.auth',  # Authentication framework
    'django.contrib.contenttypes',  # Content types framework
    'django.contrib.sessions',  # Session framework
    'django.contrib.messages',  # Messaging framework
    'django.contrib.staticfiles',  # Static files app
    'rest_framework',  # Django REST Framework for API development
    'core',  # Core application
    'users',  # Custom user management
    'corsheaders',  # Cross-Origin Resource Sharing (CORS) headers
    'channels',  # Django Channels for WebSockets
    'game',  # Game logic
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',  # Security enhancements
    'django.contrib.sessions.middleware.SessionMiddleware',  # Session management
    'django.middleware.common.CommonMiddleware',  # General HTTP middleware
    'django.contrib.auth.middleware.AuthenticationMiddleware',  # Authentication middleware
    'django.contrib.messages.middleware.MessageMiddleware',  # Messaging middleware
    'django.middleware.clickjacking.XFrameOptionsMiddleware',  # Clickjacking protection
    'allauth.account.middleware.AccountMiddleware',  # Middleware for 3rd-party OAuth
    'corsheaders.middleware.CorsMiddleware',  # CORS headers middleware
    'django.middleware.common.CommonMiddleware',  # Handles common HTTP request/response
]

ROOT_URLCONF = 'ft_transcendance.urls'  # Main URL configuration

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Path to template files
        'APP_DIRS': True,  # Enable auto-loading of app templates
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

# WSGI and ASGI applications
WSGI_APPLICATION = 'ft_transcendance.wsgi.application'
ASGI_APPLICATION = 'ft_transcendance.routing.application'  # Required for WebSockets

# Database configuration (PostgreSQL)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',  # PostgreSQL backend
        'NAME': os.getenv('DB_NAME'),  # Database name
        'USER': os.getenv('DB_USER'),  # PostgreSQL user
        'PASSWORD': os.getenv('DB_PASSWORD'),  # PostgreSQL password
        'HOST': os.getenv('DB_HOST'),  # Database host (Docker Compose service name)
        'PORT': os.getenv('DB_PORT'),  # PostgreSQL port
        'OPTIONS': {
            'connect_timeout': 10,  # Retry connection for 10 seconds
        },
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',  # Enforces password length
    },
]

# Internationalization settings
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files settings
STATIC_URL = 'static/'  # URL prefix for static files
STATIC_ROOT = BASE_DIR / 'staticfiles'  # Directory to collect static files for production

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'users.permissions.CsrfExemptSessionAuthentication',  # Custom CSRF-exempt auth
        'rest_framework.authentication.BasicAuthentication',  # Basic authentication
        'rest_framework_simplejwt.authentication.JWTAuthentication',  # JWT-based auth
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticatedOrReadOnly',  # Authenticated users can write; others read-only
    )
}

# Custom user model
AUTH_USER_MODEL = 'users.TranscendenceUser'

# 42 OAuth integration
INSTALLED_APPS += [
    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.oauth2',
    'rest_framework_simplejwt.token_blacklist',
]

# OAuth and JWT settings
SITE_ID = 1
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',  # Default auth backend
    'allauth.account.auth_backends.AuthenticationBackend',  # OAuth2 backend
)
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=int(os.getenv('ACCESS_TOKEN_LIFETIME'))),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=int(os.getenv('REFRESH_TOKEN_LIFETIME'))),
    'ROTATE_REFRESH_TOKENS': os.getenv('ROTATE_REFRESH_TOKENS') == 'True',
    'BLACKLIST_AFTER_ROTATION': os.getenv('BLACKLIST_AFTER_ROTATION') == 'True',
}

# Email settings (using Gmail SMTP)
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.getenv('EMAIL_HOST')
EMAIL_PORT = int(os.getenv('EMAIL_PORT'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS') == 'True'
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD')  # App-specific password for Gmail
DEFAULT_FROM_MAIL = os.getenv('DEFAULT_FROM_MAIL')

# Two-factor authentication
INSTALLED_APPS += [
    'django_otp',
    'django_otp.plugins.otp_totp',  # TOTP-based 2FA
    'two_factor',  # Two-factor authentication
]
MIDDLEWARE += [
    'django_otp.middleware.OTPMiddleware',  # Middleware for OTP validation
]
TWO_FACTOR_AUTHENTICATION = {
    'LOGIN_URL': 'two_factor:login',  # Redirect URL for 2FA login
    'TOTP_ISSUER': 'ft_transcendence',  # Issuer for OTP
}

# CORS settings (Cross-Origin Resource Sharing)
CORS_ALLOWED_ORIGINS = os.getenv('CORS_ALLOWED_ORIGINS', '').split(',')

CORS_ALLOW_ALL_ORIGINS = True

# Middleware for tracking last activity
MIDDLEWARE += [
    'users.tasks.UpdateLastActivityMiddleware',
]

# Custom form settings
FORM_SETTINGS = {
    'username_length_min': 3,
    'username_length_max': 15,
    'displayname_length_min': 3,
    'displayname_length_max': 15,
    'bio_length_max': 15,
}

# Celery configuration (task queue)
INSTALLED_APPS += [
    'django_celery_results',  # Stores Celery task results
    'django_celery_beat',  # Periodic task scheduler
]

CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL')
CELERY_RESULT_BACKEND = os.getenv('CELERY_RESULT_BACKEND')
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [os.getenv('REDIS_HOST'), int(os.getenv('REDIS_PORT'))],
        },
    },
}
CELERY_ACCEPT_CONTENT = ['json']  # Accept JSON task data
CELERY_TASK_SERIALIZER = 'json'  # Serialize tasks in JSON
CELERY_TIMEZONE = 'UTC'  # Timezone for Celery

# Security settings for HTTPS
SECURE_SSL_REDIRECT = True  # Redirect all HTTP requests to HTTPS
SECURE_HSTS_SECONDS = 31536000  # HTTP Strict Transport Security (1 year)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')  # Trust SSL from a proxy

# Authentication flow
LOGIN_URL = '/api/accounts/login/'  # Login URL
LOGIN_REDIRECT_URL = '/api/accounts/profile/'  # Redirect after login
LOGOUT_REDIRECT_URL = '/api/accounts/login/'  # Redirect after logout
