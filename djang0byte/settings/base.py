# -*- coding: utf-8 -*-
import os.path

# Django settings for djang0byte project.


# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/Moscow'
DATETIME_FORMAT = 'd.m.Y H:i'
# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'ru-ru'

USE_I18N = True
USE_L10N = False
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
MEDIA_URL = '/media/'
URL_FILEBROWSER_MEDIA = '/media/filebrowser/'
ADMIN_MEDIA_PREFIX = '/media/admin/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
    'django.template.loaders.eggs.load_template_source',
    )

TEMPLATE_CONTEXT_PROCESSORS = (
    'main.context_processors.djbyte',
    'main.context_processors.permission',
    'django.core.context_processors.auth',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.contrib.messages.context_processors.messages',
    'django.core.context_processors.request',
    'messages.context_processors.inbox',
    )

MIDDLEWARE_CLASSES = (
    'johnny.middleware.LocalStoreClearMiddleware',
    'johnny.middleware.QueryCacheMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.cache.CacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'main.middleware.BansMiddleware',
    )

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
    os.path.join(os.path.dirname(__file__), 'register', 'templates'),
    "/usr/lib/pymodules/python2.6/django/contrib/admin/templates/",
    )

TAGGING_AUTOCOMPLETE_JS_BASE_URL = '/media/script/jquery-autocomplete/'

INSTALLED_APPS = (
    'timezones',
    'tagging',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'registration',
    'captcha',
    'register',
    'treebeard',
    'main',
    'parser',
    'treemenus',
    'feed',
    'annoying',
    'simplepagination',
    'messages',
    'south',
    'tagging_autocomplete',
    'pytils',
    'django_push',
    'compressor',
    'sendmail',
    'johnny',
    'loginza',
    'django_evolution',
    'haystack',
)

MAN_IN_BLACKLIST = (
    'main_spy',
    'main_favourite',
    'main_lastvisit',
)

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'loginza.authentication.LoginzaBackend',
)

LOGINZA_AMNESIA_PATHS = (
    '/accounts/login/',
    '/accounts/login/js/'
)

HAYSTACK_SITECONF = 'search'
HAYSTACK_SEARCH_ENGINE = 'xapian'