# -*- coding: utf-8 -*-
import os.path
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../../"),
)

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
MEDIA_ROOT = os.path.join(PROJECT_ROOT, 'media')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

URL_FILEBROWSER_MEDIA = '/media/filebrowser/'
ADMIN_MEDIA_PREFIX = '/media/admin/'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.media',
    'django.core.context_processors.static',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    "django.core.context_processors.request",
    "django.core.context_processors.csrf",
    'django.contrib.auth.context_processors.auth',
    'django.contrib.messages.context_processors.messages',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.gzip.GZipMiddleware',
    'django.middleware.cache.CacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'accounts.middleware.GlobalRequest',
    'tools.compressor.middleware.CompressorMiddleware',
)

ROOT_URLCONF = 'urls'

TAGGING_AUTOCOMPLETE_JS_BASE_URL = '/media/script/jquery-autocomplete/'

INSTALLED_APPS = (
    # 'timezones',
    'tagging',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    'django.contrib.admindocs',
    'jsonrpc',
    # 'registration',
    # 'captcha',
    # 'register',
    # 'treebeard',
    # 'main',
    # 'treemenus',
    # 'feed',
    # 'annoying',
    # 'simplepagination',
    # 'messages',
    # 'tagging_autocomplete',
    # 'pytils',
    # 'django_push',
    # 'compressor',
    # 'loginza',
    'django_evolution',
    'tools.compressor',
    'tools.object_permissions',
    'accounts',
    'messaging',
    # 'haystack',
    # 'djang0parser',
    # 'baseutils',
    'blogging',
)

# MAN_IN_BLACKLIST = (
#     'main_spy',
#     'main_favourite',
#     'main_lastvisit',
# )

AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    # 'loginza.authentication.LoginzaBackend',
)

LOGINZA_AMNESIA_PATHS = (
    '/accounts/login/',
    '/accounts/login/js/'
)

HAYSTACK_SITECONF = 'search'
HAYSTACK_SEARCH_ENGINE = 'xapian'
PUSH_HUB = ''
