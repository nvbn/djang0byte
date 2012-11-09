from tools.compressor.base import compressor
from tools.compressor.consts import COMPRESSOR_MODE_INLINE, \
    COMPRESSOR_MODE_ONE_FILE, COMPRESSOR_ONE_FILE_IGNORE, COMPRESSOR_CACHE_ROOT, \
    COMPRESSOR_CACHE_URL, FILE_MARKER, COMPRESSOR_MODE_LINKS
from tools.compressor.obfuscators import get_obfuscator_js, get_obfuscator_css
from tools.compressor.utils import search_media
from django.conf import settings
import os
import re
import shutil
import zlib
import codecs


#TODO: add CssAbsoluteFilter -  A filter that normalizes the URLs used in ``url()`` CSS statements.


class BaseProcessor(object):
    CSS_KILL = re.compile(r"\s+")

    def allowed_types(self):
        return ["css", "js"]

    def make_obfuscation(self, phase, data):
        if compressor.get_obfuscation(phase):
            if phase == 'css':
                return get_obfuscator_css()(data)

            elif phase == 'js':
                return get_obfuscator_js()(data)

        return data

    def html(self, phase, url):
        if phase == 'css':
            return "<link rel='stylesheet' type='text/css' href='%s'/>" % url

        if phase == 'js':
            return "<script type=\"text/javascript\" src=\"%s\" charset=\"UTF-8\"></script>" % url
        return url

    def copy_to_media(self, file):
        full_filename = search_media(file)

        if full_filename.startswith(settings.MEDIA_ROOT):
            return os.path.join(
                settings.MEDIA_URL,
                full_filename.replace(settings.MEDIA_ROOT, ''),
            )
            # return settings.MEDIA_URL + full_filename[len(settings.MEDIA_ROOT)+1:]

        new_filename = "%s%s" % (zlib.adler32(full_filename) & 0xffffffff, file[file.rfind("."):])
        shutil.copyfile(full_filename, os.path.join(COMPRESSOR_CACHE_ROOT, new_filename))
        return COMPRESSOR_CACHE_URL + new_filename

    def make_cache(self, medi_type):
        #check cache
        compress_files = []
        for file in compressor.get(medi_type):
            if file in COMPRESSOR_ONE_FILE_IGNORE:
                compressor.content_add(self.html(medi_type, self.copy_to_media(file)))
            else:
                compress_files.append(search_media(file))

        max_mtime = max(map(lambda file: os.stat(file).st_mtime, compress_files))

        key = zlib.adler32("_".join(compress_files)) & 0xffffffff
        name = "%s_%s.%s" % (key, int(max_mtime), medi_type)
        cache_name = os.path.join(COMPRESSOR_CACHE_ROOT, name)
        cache_url = COMPRESSOR_CACHE_URL + name

        if not os.path.isfile(cache_name):
            #make file
            pattern = re.compile(r"^%s_(\d+).%s$" % (key, medi_type))

            #check and delete old cached CSS style
            for f in os.listdir(COMPRESSOR_CACHE_ROOT):
                if pattern.match(f):
                    os.unlink(os.path.join(COMPRESSOR_CACHE_ROOT, f))

            content = []
            for file in compress_files:
                try:
                    f = codecs.open(file, "r", "utf-8")
                    if medi_type == "js":
                        content.append(FILE_MARKER + file)
                    content.append(f.read())
                    f.close()
                except IOError, e:
                    raise Exception("Can't find '%s'\n%s" % (file, e))

#
            data = self.make_obfuscation(medi_type, "\n".join(content))

            error_happend = False
            f = open(cache_name, "w")
            try:
                f.write(data)
            except Exception, e:
                error_happend = True

            if error_happend:
                try:
                    f.write(data.encode("utf-8"))
                except Exception, e:
                    f.close()
                    os.unlink(cache_name)
                    raise e

            f.close()

            return cache_name, cache_url, data

        return cache_name, cache_url, None


class OneFile(BaseProcessor):

    def compress(self, phase):
        if compressor.get_mode(phase) != COMPRESSOR_MODE_ONE_FILE:
            return
        if not compressor.is_used_type(phase):
            return
        cache_name, cache_url, data = self.make_cache(phase)
        compressor.content_add(self.html(phase, cache_url))


class Inline(BaseProcessor):

    def compress(self, phase):
        if compressor.get_mode(phase) != COMPRESSOR_MODE_INLINE:
            return
        if not compressor.is_used_type(phase):
            return

        cache_name, cache_url, data = self.make_cache(phase)

        if phase == "css":
            compressor.content_add('<style type="text/css">\n<!--\n')
        elif phase == "js":
            compressor.content_add('<script type="text/javascript">//<![CDATA[\n')

        if not data:
            #load data from file cache
            f = open(cache_name)
            data = f.read()
            f.close()

        compressor.content_add(data)

        if phase == "css":
            compressor.content_add('\n-->\n</style>')
        elif phase == "js":
            compressor.content_add('//]]></script>')


class Links(BaseProcessor):

    def compress(self, phase):

        if compressor.get_mode(phase) != COMPRESSOR_MODE_LINKS:
            return
        if not compressor.is_used_type(phase):
            return

        for file in compressor.get(phase):
            compressor.content_add(self.html(phase, self.copy_to_media(file)))
