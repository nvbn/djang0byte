from bleach import clean
from lxml.html import fromstring
from django.conf import settings

ALLOWED_TAGS = getattr(settings, 'ALLOWED_TAGS', [
    'p', 'i', 'em', 'strong', 'b', 'u',
    'a', 'h3', 'pre', 'br', 'img', 'table',
    'tr', 'td', 'div', 'pre', 'span', 'cut',
    'fcut', 'iframe', 'user', 'spoiler', 'del', 
'ol', 'ul', 'li'])


ALLOWED_ATTRIBUTES = getattr(settings, 'ALLOWED_ATTRIBUTES', {
    '*': [
        'href', 'src', 'lang', 'alt', 'class',
        'name', 'id', 'style', 'title',
    ],
})


class Parser(object):
    """Parser with watcher callbacks"""
    def __init__(self):
        self._watchers = {}

    def add_watcher(self, xpath, callback):
        """Add xpath watcher"""
        self._watchers[xpath] = callback

    def parse(self, content):
        """Parse content"""
        tree = fromstring(content)
        for xpath, callback in self._watchers.items():
            for item in tree.xpath(xpath):
                callback(item)
        return clean(content, ALLOWED_TAGS, ALLOWED_ATTRIBUTES)


parser = Parser()
