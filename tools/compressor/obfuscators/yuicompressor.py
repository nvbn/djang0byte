from django.conf import settings
import os
import subprocess
import time

COMPRESS_STATIC_CLOSURE_BIN = getattr(settings, 'COMPRESSOR_YUICOMPRESSOR_BIN', "java -jar " + os.path.join(os.path.dirname(__file__), "..", "bin", "yuicompressor-2.4.6.jar"))


def obfuscator(content, type):
    if settings.DEBUG:
        begin = time.time()
        print "YuiCompressor: run obfuscator..."

    p = subprocess.Popen(COMPRESS_STATIC_CLOSURE_BIN + " --type %s" % type, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    p.stdin.write(content.encode('utf-8'))
    p.stdin.close()

    new_content = p.stdout.read()
    p.stdout.close()

    errors = p.stderr.read()
    p.stderr.close()
#
    if settings.DEBUG:
        old_len = len(content)
        new_len = len(new_content)
        delta = old_len - new_len

        print "YuiCompressor: source content size:", old_len
        print "YuiCompressor: new content size:", new_len
        print "YuiCompressor: compression: %s%%" % (delta * 100 / old_len)
        print "YuiCompressor: finish obfuscator - ", time.time() - begin, "s."

    return new_content


def obfuscator_js(content):
    return obfuscator(content, "js")


def obfuscator_css(content):
    return obfuscator(content, "css")
