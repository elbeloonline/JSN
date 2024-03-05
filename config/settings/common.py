# -*- coding: utf-8 -*-
"""
Django settings for jsnetwork project.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""


import environ

ROOT_DIR = environ.Path(__file__) - 3  # (jsnetwork_project/config/settings/common.py - 3 = jsnetwork_project/)
APPS_DIR = ROOT_DIR.path('jsnetwork_project')

env = environ.Env()

# APP CONFIGURATION
# ------------------------------------------------------------------------------
DJANGO_APPS = (
    # Default Django apps:
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Useful template tags:
    # 'django.contrib.humanize',

    # Admin
    'django.contrib.admin',
)
THIRD_PARTY_APPS = (
    'crispy_forms',  # Form layouts
    'allauth',  # registration
    'allauth.account',  # registration
    'allauth.socialaccount',  # registration
    # Extras
    'django_tables2', # paginated table displays
    'django_filters', # django-tables query filters
    'widget_tweaks', # add classes to tamplate fields
    'django_elasticsearch_dsl', # elasticsearch
    # 'django_elasticsearch_dsl_drf',
)

# Apps specific for this project go here.
LOCAL_APPS = (
    # custom users app
    'jsnetwork_project.users.apps.UsersConfig',
    # Your stuff: custom apps go here
    'orders',
    'nameviewer',
    'statereport',
    'pacerscraper',
    'background_task',
    'patriot',
    'usermgmt',
    'dobscraper',
    'pdftools'
,)

# See: https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE CONFIGURATION
# ------------------------------------------------------------------------------
MIDDLEWARE = (
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
)

# MIGRATIONS CONFIGURATION
# ------------------------------------------------------------------------------
MIGRATION_MODULES = {
    'sites': 'jsnetwork_project.contrib.sites.migrations'
}

# DEBUG
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool('DJANGO_DEBUG', False)

# FIXTURE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-FIXTURE_DIRS
FIXTURE_DIRS = (
    str(APPS_DIR.path('fixtures')),
)

# EMAIL CONFIGURATION
# ------------------------------------------------------------------------------
EMAIL_BACKEND = env('DJANGO_EMAIL_BACKEND', default='django.core.mail.backends.smtp.EmailBackend')

# MANAGER CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#admins
ADMINS = (
    ("""Kwan Skinner""", 'kskinner@gmail.com'),
)

ALLOWED_HOSTS = ['*']

# See: https://docs.djangoproject.com/en/dev/ref/settings/#managers
MANAGERS = ADMINS

# DATABASE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#databases
# DATABASES = {
#     'default': env.db('DATABASE_URL', default='postgres:///jsnetwork_project'),
# }
# DATABASES['default']['ATOMIC_REQUESTS'] = True

# a little bit of common stuff for db aliases
NAMESEARCH_DB = 'namesearch'
BKSEARCH_DB2 = 'bksearch2'
BKSEARCH_DB3 = 'bksearch3'
BKSEARCH_DB4 = 'bksearch4'
USDCSEARCH_DB = 'usdcsearch'  # remote version of data stored entirely on instance 2
BKSEARCH_DB_COMB = 'bksearch2_comb'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jsnetwork',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    NAMESEARCH_DB: {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jsnetwork',
        'USER': 'myuser',
        'PASSWORD': 'centralpagegarden',
        # 'HOST': 'ec2-34-226-215-155.compute-1.amazonaws.com',   # Or an IP Address that your DB is hosted on
        'HOST': 'ec2-107-20-71-205.compute-1.amazonaws.com',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    BKSEARCH_DB2: {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jsnetwork',
        'USER': 'myuser',
        'PASSWORD': 'centralpagegarden',
        'HOST': 'ec2-34-207-89-110.compute-1.amazonaws.com',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    BKSEARCH_DB3: {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jsnetwork',
        'USER': 'myuser',
        'PASSWORD': 'centralpagegarden',
        'HOST': 'ec2-3-82-231-143.compute-1.amazonaws.com',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    BKSEARCH_DB4: {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jsnetwork',
        'USER': 'myuser',
        'PASSWORD': 'centralpagegarden',
        'HOST': 'ec2-54-152-18-18.compute-1.amazonaws.com',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    USDCSEARCH_DB: {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jsnetwork',
        'USER': 'myuser',
        'PASSWORD': 'centralpagegarden',
        'HOST': 'ec2-34-207-89-110.compute-1.amazonaws.com',   # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },
    BKSEARCH_DB_COMB: {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'jsnetwork',
        'USER': 'myuser',
        'PASSWORD': 'centralpagegarden',
        'HOST': 'ec2-54-90-4-55.compute-1.amazonaws.com',  # Or an IP Address that your DB is hosted on
        'PORT': '3306',
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    },

}

# GENERAL CONFIGURATION
# ------------------------------------------------------------------------------
# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'America/Detroit'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = 'en-us'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#site-id
SITE_ID = 1

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-l10n
USE_L10N = True

# See: https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# TEMPLATE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-dirs
        'DIRS': [
            str(APPS_DIR.path('templates')),
        ],
        'OPTIONS': {
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-debug
            'debug': DEBUG,
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-loaders
            # https://docs.djangoproject.com/en/dev/ref/templates/api/#loader-types
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader',
            ],
            # See: https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
                # Your stuff: custom template context processors go here
                'django.template.context_processors.request'
            ],
        },
    },
]

# See: http://django-crispy-forms.readthedocs.io/en/latest/install.html#template-packs
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# STATIC FILE CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(ROOT_DIR('staticfiles'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = '/static/'

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = (
    str(APPS_DIR.path('static')),
)

# See: https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

# MEDIA CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-root
MEDIA_ROOT = str(APPS_DIR('media'))

# See: https://docs.djangoproject.com/en/dev/ref/settings/#media-url
MEDIA_URL = '/media/'

# URL Configuration
# ------------------------------------------------------------------------------
ROOT_URLCONF = 'config.urls'

# See: https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = 'config.wsgi.application'


# PASSWORD VALIDATION
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators
# ------------------------------------------------------------------------------

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

# AUTHENTICATION CONFIGURATION
# ------------------------------------------------------------------------------
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

# Some really nice defaults
ACCOUNT_AUTHENTICATION_METHOD = 'username'
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = 'none'

ACCOUNT_ALLOW_REGISTRATION = env.bool('DJANGO_ACCOUNT_ALLOW_REGISTRATION', True)
ACCOUNT_ADAPTER = 'jsnetwork_project.users.adapters.AccountAdapter'
SOCIALACCOUNT_ADAPTER = 'jsnetwork_project.users.adapters.SocialAccountAdapter'

# Custom user app defaults
# Select the correct user model
AUTH_USER_MODEL = 'users.User'
LOGIN_REDIRECT_URL = 'users:redirect'
LOGIN_URL = 'account_login'

# SLUGLIFIER
AUTOSLUG_SLUGIFY_FUNCTION = 'slugify.slugify'


# Location of root django.contrib.admin URL, use {% url 'admin:index' %}
ADMIN_URL = r'^admin/'

# Your common stuff: Below this line define 3rd party library settings
# ------------------------------------------------------------------------------

# WINWARD REPORTING ENGINE SETTINGS
WINDWARD_ENGINE_URL = 'http://ec2-34-224-57-184.compute-1.amazonaws.com:8080'

# NAME MATCH DATABASE SETTINGS
NAME_MATCH_SCORE_DEFAULT = 87
FIRST_NAME_MATCH_SCORE = 88


# EMAIL FETCHER SETTINGS
FETCH_MAIL_SERVER = 'mail.judgmentsearchnetwork.com'
MAIL_LOGIN = 'data1@judgmentsearchnetwork.com'
MAIL_PASSWORD = 'q7sLy5xFUM_M?<'
EMAIL_ARCHIVE_FOLDER = 'INBOX.Archive'
EMAIL_DATA_DIR = 'email_data'
EMAIL_COPY_TO_DIR = 'email_copied'


# LOGGING CONFIGURATION
# ------------------------------------------------------------------------------
# See: https://docs.djangoproject.com/en/dev/ref/settings/#logging
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# https://gist.github.com/st4lk/6725777
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        },
        'require_debug_true': {
            '()': 'django.utils.log.RequireDebugTrue'
        }
    },
    'formatters': {
        # 'main_formatter': {
        #     'format': '%(levelname)s:%(name)s: %(message)s '
        #               '(%(asctime)s; %(filename)s:%(lineno)d)',
        #     'datefmt': "%Y-%m-%d %H:%M:%S",
        # },
        'main_formatter': {
            'format': '%(levelname)s:(%(asctime)s): %(message)s ',
            'datefmt': "%Y-%m-%d %H:%M:%S",
        },
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'console': {
            'level': 'INFO',
            # 'filters': ['require_debug_true'],
            'class': 'logging.StreamHandler',
            'formatter': 'main_formatter',
        },
        'production_file': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/bankruptcy_scraper.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 7,
            'formatter': 'main_formatter',
            'filters': ['require_debug_false'],
        },
        'debug_file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': 'logs/bankruptcy_scraper_debug.log',
            'maxBytes': 1024 * 1024 * 5,  # 5 MB
            'backupCount': 7,
            'formatter': 'main_formatter',
            'filters': ['require_debug_true'],
        },
        'null': {
            "class": 'logging.NullHandler',
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins', 'console'],
            'level': 'ERROR',
            'propagate': True,
        },
        'django': {
            'handlers': ['null', ],
        },
        'py.warnings': {
            'handlers': ['null', ],
        },
        '': {
            'handlers': ['console', 'production_file', 'debug_file'],
            'level': "DEBUG",
        },
    },
}

# TASK/QUEUE MANAGER SETTINGS
MAX_ATTEMPTS = 1

# DOB SCRAPER SETTINGS
# DOB_SERVER_URL = "http://localhost:8080"
DOB_SERVER_URL = "http://ec2-35-172-231-61.compute-1.amazonaws.com:8080"
DOB_POST_JOB_ENDPOINT = DOB_SERVER_URL + "/order_judgments/"
DOB_JOB_STATUS_ENDPOINT = DOB_SERVER_URL + "/scrape_status/{}/?format=json"
DOB_JOB_RESULT_ENDPOINT = DOB_SERVER_URL + "/scraped_dobs/{}/?format=json"
RUN_DOB_SEARCH = None


# ELASTICSEARCH
ELASTICSEARCH_DSL = {
    'default': {
        'hosts': '107.20.71.205:9200'
    },
}

USE_ELASTICSEARCH_SCNJ = False
USE_ELASTICSEARCH_BKCY = False

BKCY_REPORT_EXACT_MATCH_ONLY = True

MERGE_PDF_SCRAPED_PARTY_INFO = True
