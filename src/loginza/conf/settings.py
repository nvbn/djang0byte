# -*- coding:utf-8 -*-
from django.conf import settings

lang = 'en'
if 'ru' in settings.LANGUAGE_CODE: lang = 'ru'
elif 'uk' in settings.LANGUAGE_CODE: lang = 'uk'
# Default language that wil be used for loginza widgets when not explicitly set for widget template tag.
DEFAULT_LANGUAGE = getattr(settings, 'LOGINZA_DEFAULT_LANGUAGE', lang)

# Comma separated providers list, that will be used for widgets w/out providers_set parameter explicitly set.
DEFAULT_PROVIDERS_SET = getattr(settings, 'LOGINZA_DEFAULT_PROVIDERS_SET', None)

# Default provider for widgets w/out provider parameter explicitly set.
DEFAULT_PROVIDER = getattr(settings, 'LOGINZA_DEFAULT_PROVIDER', None)

# Comma-separated providers names for providers icons that will be shown for loginza_icons widget.
# Only used when providers_set is not set for widget template tag and DEFAULT_PROVIDERS_SET is None.
# When empty - all available providers icons will be shown.
ICONS_PROVIDERS = getattr(settings, 'LOGINZA_ICONS_PROVIDERS', None)

# Dict with keys as provider names and values as provider titles to use as alt and title
# for loginza_icons widget. Values will be used to override default titles.
PROVIDER_TITLES = getattr(settings, 'LOGINZA_PROVIDER_TITLES', {})

# Default email that will be used for new users when loginza data does not have one.
DEFAULT_EMAIL = getattr(settings, 'LOGINZA_DEFAULT_EMAIL', 'user@loginza')

# List or tuple of paths, that will not be stored for return.
AMNESIA_PATHS = getattr(settings, 'LOGINZA_AMNESIA_PATHS', ())

# Button widget image url.
BUTTON_IMG_URL = getattr(settings, 'LOGINZA_BUTTON_IMG_URL', 'http://loginza.ru/img/sign_in_button_gray.gif')

# Icons widget images urls.
ICONS_IMG_URLS = getattr(settings, 'LOGINZA_ICONS_IMG_URLS', {})