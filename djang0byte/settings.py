# -*- coding: utf-8 -*-
import os.path

# Django settings for djang0byte project.
DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
     ('Vladimir Yakovlev', 'nvbn.rm@gmail.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'mysql'#'postgresql_psycopg2'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'dbyte'             # Or path to database file if using sqlite3.
DATABASE_USER = 'root'             # Not used with sqlite3.
DATABASE_PASSWORD = 'qazwsx'         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

JOHNNY_MIDDLEWARE_KEY_PREFIX = 'my_project1_jonny_cache_key'
#CACHE_BACKEND = 'johnny.backends.memcached://localhost:11211'

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

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True
USE_L10N = False
MEDIA_ROOT = '/home/nvbn/work/djang0byte/djang0byte/media/'
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
MEDIA_URL = '/media/'
URL_FILEBROWSER_MEDIA = '/media/filebrowser/'
ADMIN_MEDIA_PREFIX = '/media/admin/'


# Make this unique, and don't share it with anybody.
SECRET_KEY = 'r25ofx1lr43d%0yzcwfeog5nxed0^!fe4ck)w!r6et@qejhx*6'

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
    'debug_toolbar.middleware.DebugToolbarMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates'),
    os.path.join(os.path.dirname(__file__),'register' ,'templates'),
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
'debug_toolbar',
'johnny',
)
KEYWORD_MIN_COUNT = 50
PUBSUB = False
EMAIL_HOST = 'localhost'
DEFAULT_FROM_EMAIL = 'webmaster@localhost'
ACCOUNT_ACTIVATION_DAYS = 7
AUTH_PROFILE_MODULE = "main.profile"
VALID_TAGS = 'p i em strong b u a h3 pre br img table tr td div pre span cut fcut iframe user spoiler'
VALID_ATTRS = 'href src lang alt class name id style'
DEFAULT_BLOG_TYPE = 'main'
NEWPOST_RATE = 0
NEWBLOG_RATE = 0
NEWCOMMENT_RATE = 0
RATEPOST_RATE = 0
RATECOM_RATE = 0
RATEUSER_RATE = 0
RATEBLOG_RATE = 0
POST_RATE_COEFFICIENT = 0.3
BLOG_RATE_COEFFICIENT = 0.2
COMMENT_RATE_COEFFICIENT = 0.1
DEFAULT_CACHE_TIME = 0
MENU_CACHE_TIME = 0
SIDEBAR_CACHE_TIME = 0
DEFAULT_AVATAR = '/media/style/figure.gif'
LOGIN_REDIRECT_URL = '/'
RECAPTCHA_PUBLIC_KEY = '6LeLNMISAAAAAI2FBbNBnjf_ms6a5werjXbTbNCk '
RECAPTCHA_PRIVATE_KEY = '6LeLNMISAAAAAMassCnG27qheWXn7Fr_ePSvMP6r '
SITENAME = 'Djang0byte is a capital of'
POST_RATE_TO_MAIN = 0
PUSH_HUB = u'http://pubsubhubbub.appspot.com/'
FEED_URL = u'http://localhost/rss/'
DOMAIN_NAME = 'localhost'
COMPRESS_PARSER = 'compressor.parser.LxmlParser'
COMPRESS = True
COMPRESS_YUI_BINARY = '/usr/bin/yui-compressor'
COMPRESS_CSS_FILTERS = ['compressor.filters.yui.YUICSSFilter',]
API_KEY = "API_KEY"
FULLNAME = 'Full site name'
ONLINE_TIME = 600
MAN_IN_BLACKLIST = (
'main_spy',
'main_favourite',
'main_lastvisit',
)
"""
INTERNAL_IPS = ('127.0.0.1:8000',)
def custom_show_toolbar(request):
    return True # Always show toolbar, for example purposes only.
DEBUG_TOOLBAR_CONFIG = {
    'INTERCEPT_REDIRECTS': False,
    'SHOW_TOOLBAR_CALLBACK': custom_show_toolbar,
}"""