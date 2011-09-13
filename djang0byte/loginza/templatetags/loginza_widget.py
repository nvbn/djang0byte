# -*- coding:utf-8 -*-
import urllib

from django.contrib.sites.models import Site
from django.core.urlresolvers import reverse
from django.template import Library, Node, TemplateSyntaxError
from django.template.defaulttags import kwarg_re
from django.utils.encoding import smart_str

from loginza.conf import settings

register = Library()

allowed_providers_def = {
    'google': u'Google Accounts',
    'yandex': u'Yandex',
    'mailruapi': u'Mail.ru API',
    'mailru': u'Mail.ru',
    'vkontakte': u'Вконтакте',
    'facebook': u'Facebook',
    'twitter': u'Twitter',
    'loginza': u'Loginza',
    'myopenid': u'MyOpenID',
    'webmoney': u'WebMoney',
    'rambler': u'Rambler',
    'flickr': u'Flickr',
    'lastfm': u'Last.fm',
    'verisign': u'Verisign',
    'aol': u'AOL',
    'steam': u'Steam',
    'openid': u'OpenID'
}

allowed_providers = {}
for key, value in allowed_providers_def.items():
    allowed_providers[key] = settings.PROVIDER_TITLES.get(key, value)

def _return_path(request, path=None):
    if path is not None and path not in settings.AMNESIA_PATHS:
        request.session['loginza_return_path'] = path
    return request.session.get('loginza_return_path', '/')


def _absolute_url(url):
    return 'http://%s%s' % (Site.objects.get_current().domain, url)


def return_url():
    return urllib.quote(_absolute_url(reverse('loginza.views.return_callback')), '')


def _providers_set(kwargs):
    providers_set = []

    providers_list = kwargs['providers_set'] if 'providers_set' in kwargs else settings.DEFAULT_PROVIDERS_SET
    if providers_list is not None:
        providers = providers_list.split(',')
        for provider in providers:
            if provider in allowed_providers:
                providers_set.append(provider)

    return providers_set


def providers(kwargs):
    params = []

    providers_set = _providers_set(kwargs)
    if len(providers_set) > 0:
        params.append('providers_set=' + ','.join(providers_set))

    provider = kwargs['provider'] if 'provider' in kwargs else settings.DEFAULT_PROVIDER
    if provider in allowed_providers:
        params.append('provider=' + provider)

    return ('&'.join(params) + '&') if len(params) > 0 else ''


def iframe_template(kwargs, caption=''):
    return """<script src="http://loginza.ru/js/widget.js" type="text/javascript"></script>
<iframe src="http://loginza.ru/api/widget?overlay=loginza&%(providers)slang=%(lang)s&token_url=%(return-url)s"
style="width:359px;height:300px;" scrolling="no" frameborder="no"></iframe>""" % {
        'return-url': return_url(),
        'lang': kwargs['lang'],
        'providers': providers(kwargs),
        'caption': caption
    }


def button_template(kwargs, caption):
    return """<script src="http://loginza.ru/js/widget.js" type="text/javascript"></script>
<a href="http://loginza.ru/api/widget?%(providers)slang=%(lang)s&token_url=%(return-url)s" class="loginza">
    <img src="%(button-img)s" alt="%(caption)s" title="%(caption)s"/>
</a>""" % {
        'button-img': settings.BUTTON_IMG_URL,
        'return-url': return_url(),
        'caption': caption,
        'lang': kwargs['lang'],
        'providers': providers(kwargs)
    }


def icons_template(kwargs, caption):
    def icons():
        providers_set = _providers_set(kwargs)
        # if providers set is not set explicitly - all providers are used
        if len(providers_set) < 1:
            setting_icons = settings.ICONS_PROVIDERS
            providers_set = setting_icons.split(',') if setting_icons is not None else allowed_providers.keys()

        imgs = []
        for provider in providers_set:
            # TODO: remove this workaround after Loginza will fix issue with disappeared icons
            # see http://feedback.loginza.ru/problem/details/id/2648

            # commenting this workaroud as now we have way to override missed icons urls
            # if provider in ('verisign', 'aol'): continue

            if provider in settings.ICONS_IMG_URLS: img_url = settings.ICONS_IMG_URLS[provider]
            else: img_url = 'http://loginza.ru/img/providers/%s.png' % provider

            imgs.append('<img src="%(img_url)s" alt="%(title)s" title="%(title)s">' % {
                'img_url': img_url,
                'title': allowed_providers[provider]
            })
        return '\r\n'.join(imgs)

    return """<script src="http://loginza.ru/js/widget.js" type="text/javascript"></script>
%(caption)s
<a href="https://loginza.ru/api/widget?%(providers)slang=%(lang)s&token_url=%(return-url)s" class="loginza">
    %(icons)s
</a>""" % {
        'return-url': return_url(),
        'caption': caption,
        'lang': kwargs['lang'],
        'providers': providers(kwargs),
        'icons': icons()
    }


def string_template(kwargs, caption):
    return """<script src="http://loginza.ru/js/widget.js" type="text/javascript"></script>
<a href="http://loginza.ru/api/widget?%(providers)slang=%(lang)s&token_url=%(return-url)s" class="loginza">
    %(caption)s"
</a>""" % {
        'return-url': return_url(),
        'caption': caption,
        'lang': kwargs['lang'],
        'providers': providers(kwargs)
    }


class LoginzaWidgetNode(Node):
    def __init__(self, html_template, caption, kwargs, asvar):
        self.html_template = html_template
        self.caption = caption
        self.kwargs = kwargs
        self.asvar = asvar

    def render(self, context):
        kwargs = dict([(smart_str(k, 'ascii'), v.resolve(context))
                       for k, v in self.kwargs.items()])
        if 'lang' not in kwargs:
            kwargs['lang'] = settings.DEFAULT_LANGUAGE

        # save current path, so if user will be logged with loginza
        # he will be redirected back to the page he for login
        _return_path(context['request'], context['request'].path)

        html = self.html_template(kwargs, self.caption)
        if self.asvar:
            context[self.asvar] = html
            html = ''

        return html


def _loginza_widget(parser, token, html_template):
    def unquote(s):
        if s[0] in ('"', "'"): s = s[1:]
        if s[-1] in ('"', "'"): s = s[:-1]
        return s

    bits = token.split_contents()
    if len(bits) < 2:
        if html_template != iframe_template:
            raise TemplateSyntaxError("'%s' takes at least one argument"
                                      " (caption)" % bits[0])
        else:
            caption = ''
    else:
        caption = unquote(bits[1])

    kwargs = {}
    asvar = None
    if len(bits) >= 2 and bits[-2] == 'as':
        asvar = bits[-1]
        bits = bits[:-2]

    # Now all the bits are parsed into new format,
    # process them as template vars
    if len(bits):
        for bit in bits:
            match = kwarg_re.match(bit)
            if not match:
                raise TemplateSyntaxError("Malformed arguments to loginza widget tag")
            name, value = match.groups()
            kwargs[name] = parser.compile_filter(value)

    return LoginzaWidgetNode(html_template, caption, kwargs, asvar)


@register.tag
def loginza_iframe(parser, token):
    return _loginza_widget(parser, token, iframe_template)


@register.tag
def loginza_button(parser, token):
    return _loginza_widget(parser, token, button_template)


@register.tag
def loginza_icons(parser, token):
    return _loginza_widget(parser, token, icons_template)


@register.tag
def loginza_string(parser, token):
    return _loginza_widget(parser, token, string_template)
