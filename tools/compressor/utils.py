import os
from django.conf import settings
from tools.compressor.class_loader import app_path_by_name
import re
from django.core.cache import cache
from django.conf import settings
from tools.compressor.base import compressor


COMPRESSOR_USE_CACHE_FOR_SEARCH_MEDIA = getattr(settings, "COMPRESSOR_USE_CACHE_FOR_SEARCH_MEDIA", False)
COMPRESSOR_CHACE_PREFIX = "compr_"


def search_media(value):
    #check full path
    if os.path.exists(value):
        return value

    if COMPRESSOR_USE_CACHE_FOR_SEARCH_MEDIA:
        ret = cache.get("%s|%s" % (COMPRESSOR_CHACE_PREFIX, value), -1)
        if ret != -1:
            return ret

    path_name = os.path.join(settings.MEDIA_ROOT, value)
    if os.path.exists(path_name):
        if COMPRESSOR_USE_CACHE_FOR_SEARCH_MEDIA:
            cache.set("%s|%s" % (COMPRESSOR_CHACE_PREFIX, value), path_name)
        return path_name

    for apps in settings.INSTALLED_APPS:
        path_name = os.path.join(app_path_by_name(apps), 'media', value)
        if os.path.exists(path_name):
            if COMPRESSOR_USE_CACHE_FOR_SEARCH_MEDIA:
                cache.set("%s|%s" % (COMPRESSOR_CHACE_PREFIX, value), path_name)
            return path_name

    path_name = os.path.join(settings.STATIC_ROOT, value)
    if os.path.exists(path_name):
        if COMPRESSOR_USE_CACHE_FOR_SEARCH_MEDIA:
            cache.set("%s|%s" % (COMPRESSOR_CHACE_PREFIX, value), path_name)
        return path_name

    return None


def include_js(file_name):
    full_name = search_media(file_name)
    f = open(full_name, "rt")
    data = f.read()
    f.close()

    res = include_js.pattern.findall(data)
    if res:
        for name in res:
            add_to_compress(name)

include_js.pattern = re.compile("//include \"(.+)\"")


def add_to_compress(value):
    """add to compress pattern of file name.
    arguments:
    value - pattern of file name, use '/path/to/file/*' for add all ccs & js files to compresssor
    """

    if not value:
        return
    if value.endswith("*"):
        #Find path templates in app
        start_value = value[:-1]
        for apps in settings.INSTALLED_APPS:
            base_path = os.path.join(os.path.join(settings.PROJECT_SRC_ROOT, *apps.split(".")), 'media')
            path_name = os.path.join(base_path, start_value)
            if os.path.exists(path_name):
                for sub_path in os.walk(path_name):
                    for file in sub_path[2]:
                        final_path = os.path.join(sub_path[0], file)
                        if final_path.endswith(".css") or final_path.endswith(".js"):
                            value = final_path[len(base_path) + 1:]
                            add_to_compress(value)
        return
    else:
        type = value[value.rfind('.') + 1:].lower()
        assert type in compressor.allowed_types, "Unknown compress type '%s';\nFile '%s';\nExist types: %s" % (type, value, unicode(compressor.allowed_types))

    #check file exists
    if settings.DEBUG:
        if search_media(value) is None:
            raise Exception("Not found '%s'" % value)

    if not compressor.has(type, value):
        include_js(value)
        compressor.append(type, value)
