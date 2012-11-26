# coding=utf-8
from tools.compressor.base import compressor
from tools.compressor.consts import COMPRESSOR_MODE_INLINE, COMPRESSOR_MODE_LINKS, \
    COMPRESSOR_MODE_ONE_FILE, COMPRESSOR_MARKER
from tools.compressor.utils import add_to_compress
from django import forms, template
from django.conf import settings
from django.template import Node, Variable, VariableDoesNotExist, \
    TemplateSyntaxError
import types


#check middleware


register = template.Library()


class CompressNode(Node):
    def __init__(self, args, **kwargs):
        self.args = args

    def render(self, context):
        for arg in self.args:
            var = Variable(arg)
            try:
                value = var.resolve(context)
            except VariableDoesNotExist:
                raise TemplateSyntaxError('"compress" tag got an unknkown variable: %r' % var.var)

            if isinstance(value, forms.BaseForm):
                for js in value.media._js:
                    add_to_compress(js)

                if "" in value.media._css:
                    for css in value.media._css[""]:
                        add_to_compress(css)

                if "all" in value.media._css:
                    for css in value.media._css["all"]:
                        add_to_compress(css)
                continue

            if callable(value):
                value = value()

            if isinstance(value, (types.ListType, types.TupleType)):
                for v in value:
                    #print "ADDD:", v,"(",value,")"
                    add_to_compress(v)
            else:
                add_to_compress(value)
        return ""


def compress(parser, token):
    return CompressNode(token.contents.split()[1:])
register.tag(compress)


class CompressdResultsNode(Node):

    def __init__(self, type, args, **kwargs):
        self.args = args
        self.type = type

    def use(self, name):
        try:
            self.args.remove(name)
            return True
        except:
            return False

    def render(self, context):
#        if len(self.args)>2:
#            raise TemplateSyntaxError('"compressed_%s" wrong arguments count.' % self.type)

        if self.args:
            if self.use("inline"):
                compressor.set_mode(self.type, COMPRESSOR_MODE_INLINE)

            if self.use("links"):
                compressor.set_mode(self.type, COMPRESSOR_MODE_LINKS)

            if self.use("one_file"):
                compressor.set_mode(self.type, COMPRESSOR_MODE_ONE_FILE)

            if self.use("obfuscation=True"):
                compressor.set_obfuscation(self.type, True)

            if self.use("obfuscation=False"):
                compressor.set_obfuscation(self.type, False)

            if len(self.args) > 0 and settings.DEBUG:
                raise TemplateSyntaxError('"compressed_%s" wrong arguments %s.' % (self.type, self.args))

        return COMPRESSOR_MARKER[self.type]


def compressed_css(parser, token):
    return CompressdResultsNode("css", token.contents.split()[1:])
register.tag(compressed_css)


def compressed_js(parser, token):
    return CompressdResultsNode("js", token.contents.split()[1:])
register.tag(compressed_js)
