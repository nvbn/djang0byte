from django.conf import settings
import os


PROCESSOR_LIST = getattr(settings, "COMPRESSOR_PROCESSORS", [
    "tools.compressor.coffee_script.CoffeeCompiler",
    "tools.compressor.processors.OneFile",
    "tools.compressor.processors.Inline",
    "tools.compressor.processors.Links",
])


COMPRESSOR_MODE_ONE_FILE = 1
COMPRESSOR_MODE_LINKS = 2
COMPRESSOR_MODE_INLINE = 3


COMPRESSOR_MARKER = {
    "css": "<!--[*CSS*]-->",
    "js": "<!--[*JS*]-->"
}


COMPRESSOR_CACHE_PREFIX = "cache"

COMPRESSOR_CACHE_ROOT = getattr(settings, 'COMPRESSOR_CACHE_ROOT', os.path.join(settings.MEDIA_ROOT, COMPRESSOR_CACHE_PREFIX))
COMPRESSOR_CACHE_URL = getattr(settings, 'COMPRESSOR_CACHE_URL', settings.MEDIA_URL + COMPRESSOR_CACHE_PREFIX + '/')
COMPRESSOR_ONE_FILE_IGNORE = getattr(settings, "COMPRESSOR_ONE_FILE_IGNORE", [])

FILE_MARKER = "//__file__="
