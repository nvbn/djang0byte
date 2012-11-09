from django.conf import settings
from tools.compressor.class_loader import get_class_by_string

#DEFAULT_OBFUSCATOR = getattr(settings, "COMPRESSOR_DEFAULT_OBFUSCATOR", "compressor.obfuscators.google_closure")
DEFAULT_OBFUSCATOR = getattr(settings, "COMPRESSOR_DEFAULT_OBFUSCATOR", "compressor.obfuscators.yuicompressor")


def get_obfuscator_js():
    try:
        return get_obfuscator_js.func
    except AttributeError:
        get_obfuscator_js.func = get_class_by_string(DEFAULT_OBFUSCATOR + ".obfuscator_js")
    return get_obfuscator_js.func


def get_obfuscator_css():
    try:
        return get_obfuscator_css.func
    except AttributeError:
        get_obfuscator_css.func = get_class_by_string(DEFAULT_OBFUSCATOR + ".obfuscator_css")
    return get_obfuscator_css.func
