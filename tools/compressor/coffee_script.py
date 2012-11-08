from compressor.processors import BaseProcessor
from compressor.base import compressor
import os
import zlib
from compressor.utils import search_media
from commands import getoutput
from compressor.consts import COMPRESSOR_CACHE_ROOT, COMPRESSOR_CACHE_URL,\
    COMPRESSOR_CACHE_PREFIX
import re


class CoffeeScriptCompilationException(Exception):

    def __init__(self, error_text):
        self.error_text = error_text

    def __unicode__(self):
        return "Compilation error:\n%s" % self.error_text


class CoffeeCompiler(BaseProcessor):

    def allowed_types(self):
        return ["coffee"]

    def compress(self, phase):
        if phase == "js":  # work only with js compressor phase
            for file_name in compressor.get("coffee"):
                full_path_name = search_media(file_name)

                mtime = os.stat(full_path_name).st_mtime
                key = zlib.adler32(full_path_name) & 0xffffffff
                cache_file_name = "coffee_%s_%s.%s" % (key, int(mtime), "js")
                full_cache_name = os.path.join(COMPRESSOR_CACHE_ROOT, cache_file_name)
                if not os.path.isfile(full_cache_name):
                    print "MAKE NEW COFFEE COMPILATTION"

                    #delete old cache
                    pattern = re.compile(r"^coffee_%s_(\d+).js$" % key)
                    #check and delete old cached files
                    for f in os.listdir(COMPRESSOR_CACHE_ROOT):
                        if pattern.match(f):
                            os.unlink(os.path.join(COMPRESSOR_CACHE_ROOT, f))

                    #compile coffee script
                    output = getoutput("coffee -p %s > %s" % (full_path_name, full_cache_name))

                    if output.strip("\n") != "":
                        raise CoffeeScriptCompilationException(output)
                #check
                compressor.replace("coffee", file_name, "js", COMPRESSOR_CACHE_PREFIX + "/" + cache_file_name)
