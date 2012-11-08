from compressor.consts import FILE_MARKER
from django.conf import settings
import os
import subprocess
import time
import re

COMPRESS_STATIC_CLOSURE_BIN = getattr(settings, 'COMPRESSOR_GOOGLE_CLOSURE_BIN', "java -jar " + os.path.join(os.path.dirname(__file__), "..", "bin", "compiler.jar"))


class ObfuscatorError(Exception):

    def __init__(self, errors, content):
        self.errors = errors
        self.content = content.split("\n")

    def __unicode__(self):
        parsed = []
        unparsed = []

        for err_line in self.errors.split("stdin:"):
            if not err_line:
                continue
            err = err_line.split(":")

            if len(err) < 2:
                unparsed.append(err_line)
                continue
            line_num = int(err[0])
            #getfile name
            file_name = None
            file_line = line_num
            start_check = line_num - 1
            while not file_name and start_check:
                if self.content[start_check].startswith(FILE_MARKER):
                    file_name = self.content[start_check][len(FILE_MARKER):]
                    break
                start_check -= 1
            file_line = line_num - start_check - 1
            del err[0]

            parsed.append("\n\n%s:%s >>> \"%s\"\n\t%s" % (file_name, file_line, self.content[int(line_num - 1)], ":".join(err).strip()))

        return "GoogleClosure found errors:\n%s\n______________________\n%s" % ("\n".join(parsed), "\n".join(unparsed))


def obfuscator_js(content):
    if settings.DEBUG:
        begin = time.time()
        print "GoogleClosure: run obfuscator..."

    p = subprocess.Popen(COMPRESS_STATIC_CLOSURE_BIN + " --summary_detail_level=0 --compilation_level=ADVANCED_OPTIMIZATIONS --warning_level=QUIET", shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    p.stdin.write(content.encode('utf-8'))
    p.stdin.close()

    new_content = p.stdout.read()
    p.stdout.close()

    errors = p.stderr.read()
    p.stderr.close()

    if settings.DEBUG:
        old_len = len(content)
        new_len = len(new_content)
        delta = old_len - new_len

        print "GoogleClosure: source content size:", old_len
        print "GoogleClosure: new content size:", new_len

        print "GoogleClosure: complression: %s%%" % (delta * 100 / old_len)
        print "GoogleClosure: finish obfuscator - ", time.time() - begin, "s."

    if p.wait() != 0:
        if not errors:
            errors = 'Unable to apply Google Closure obfuscator'
        raise ObfuscatorError(errors, content)

    if len(errors) > 0:
        raise ObfuscatorError(errors, content)

    return new_content


CSS_KILL = re.compile(r"\s+")


def obfuscator_css(content):
    return CSS_KILL.sub(" ", content)
