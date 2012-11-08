from compressor.consts import COMPRESSOR_MODE_ONE_FILE, COMPRESSOR_MARKER, \
    PROCESSOR_LIST
from compressor.class_loader import get_class_by_string
from django.conf import settings
import threading
from django.utils.functional import cached_property


class Compressor():

    def __init__(self):
        self.local = threading.local()
        self.processors = []

    def clean(self):
        self.mode = {}
        self.obfuscation = {}
#        for type in self.allowed_types:
#            setattr(self.local, type, [])
        self.local = []

        #apply global config
        self.mode['css'] = getattr(settings, "COMPRESSOR_CSS_MODE", COMPRESSOR_MODE_ONE_FILE)
        self.mode['js'] = getattr(settings, "COMPRESSOR_JS_MODE", COMPRESSOR_MODE_ONE_FILE)

        self.obfuscation['css'] = getattr(settings, "COMPRESSOR_CSS_OBFUSCATION", True)
        self.obfuscation['js'] = getattr(settings, "COMPRESSOR_JS_OBFUSCATION", True)

    @cached_property
    def allowed_types(self):
        self.initialize_processors()
        types = []
        for processor in self.processors:
            for t in processor.allowed_types():
                if t not in types:
                    types.append(t)
        return types

    def has(self, type, filename):
        return (type, filename) in self.local

    def append(self, type, filename):
        self.local.append((type, filename))

    def get(self, type):
        return [file for t, file in self.local if type == t]

    def replace(self, type, filename, new_type, new_filename):
        index = self.local.index((type, filename))
        self.local.insert(index, (new_type, new_filename))
        self.local.remove((type, filename))

    def is_used(self):
        return len(self.local) > 0

    def is_used_type(self, type):
        for t, file in self.local:
            if t == type:
                return True
        return False

    def set_mode(self, type, mode):
        self.mode[type] = mode

    def get_mode(self, type):
        return self.mode[type]

    def set_obfuscation(self, type, use):
        self.obfuscation[type] = use

    def get_obfuscation(self, type):
        return self.obfuscation[type]

    def initialize_processors(self):
        if not self.processors:
            for processor_name in PROCESSOR_LIST:
                klass = get_class_by_string(processor_name)
                self.processors.append(klass())

    def compress(self, phase):
        self.initialize_processors()
        self.content = []
        for processor in self.processors:
            processor.compress(phase)
        return unicode("".join(self.content))

    def content_add(self, line):
        self.content.append(line)

compressor = Compressor()
