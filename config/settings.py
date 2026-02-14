"""
https://docs.djangoproject.com/en/6.0/topics/settings/

https://docs.djangoproject.com/en/6.0/ref/settings/
"""

from pathlib import Path
import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent


#  https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/


SECRET_KEY = 'django-insecure-$$owhb*k13)pbye%wgmkx51h*q_a!+2__91lb87rd#y&*mtxf!'


DEBUG = True

ALLOWED_HOSTS = []



INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# https://docs.djangoproject.com/en/6.0/ref/settings/#databases

env = environ.Env()

environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

DATABASES = {
    'default': env.db(),
}

"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'defaultdb',
        'USER': 'avnadmin',
        'PASSWORD': '',
        'HOST': 'dzienniknowy-jakubdb.l.aivencloud.com',
        'PORT': '22843',
        'CONN_MAX_AGE': 600,
    }
}
""""

DATABASES['default']['OPTIONS'] = {
    'sslmode': 'require',
}
"""
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'dziennik_nowy',
        'USER': 'postgres',
        'PASSWORD': 'postgres',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}
"""

# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

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

AUTH_USER_MODEL = 'core.User'
LOGIN_URL = 'login'
LOGIN_REDIRECT_URL = 'dashboard_router'
LOGOUT_REDIRECT_URL = 'login'

# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'pl'

TIME_ZONE = 'Europe/Warsaw'

USE_I18N = True

USE_TZ = True


# https://docs.djangoproject.com/en/6.0/howto/static-files/

STATIC_URL = 'static/'
