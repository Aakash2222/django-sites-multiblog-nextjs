"""
Django settings for blogproject project.

This configuration enables the Django Sites framework to support
multiple blog domains from a single backend instance.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-dev-key-change-in-production'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['blog1.com', 'blog2.com', 'localhost', '127.0.0.1']

# Trust proxy headers (needed for X-Forwarded-Host to work)
# This allows Django to detect the correct site when requests come through Next.js proxy
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = None  # Not using SSL in development


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Django Sites framework - enables multi-site support
    # This allows a single Django instance to serve multiple domains
    'django.contrib.sites',
    # Django REST Framework for API endpoints
    'rest_framework',
    # CORS headers to allow Next.js frontend to access the API
    'corsheaders',
    # Our blog application
    'blog',
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

ROOT_URLCONF = 'blogproject.urls'

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

WSGI_APPLICATION = 'blogproject.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Django Sites Framework Configuration
# ====================================
# SITE_ID is used as a default/fallback when the Sites framework needs
# to determine which site to use. However, in our implementation, we
# dynamically detect the site from the incoming HTTP request's Host header
# using get_current_site(request), so SITE_ID is mainly for:
# 1. Django admin interface initialization
# 2. Fallback scenarios
# 3. Management commands that don't have request context
#
# The actual site detection happens in our API views using:
# from django.contrib.sites.shortcuts import get_current_site
# current_site = get_current_site(request)
#
# This allows the same API endpoint to return different content based on
# the domain making the request, without any code changes.
SITE_ID = 1

# Django REST Framework Configuration
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 100
}

# CORS Configuration
# Allow requests from Next.js frontend
CORS_ALLOWED_ORIGINS = [
    "http://blog1.com:3000",
    "http://blog2.com:3000",
    "http://localhost:3000",
]

CORS_ALLOW_CREDENTIALS = True
