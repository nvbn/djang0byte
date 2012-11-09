from lxml.html import fromstring
import re
import urllib


NOT_STARTED = -1


class RemoteServiceManager(object):
    def __init__(self):
        self._registered = []
        self._default = None

    def get_service(self, url):
        for regexp, service in self._registered:
            if regexp.match(url):
                return service(url)
        return self._default(url)


manager = RemoteServiceManager()
get_service = manager.get_service


class BaseRemoteService(type):
    def __new__(cls, name, parents, attrs):
        result = type.__new__(cls, name, parents, attrs)
        if attrs.get('__default__'):
            manager._default = result
        if attrs.get('__regexp__'):
            attrs['__regexp__'] = re.compile(attrs['__regexp__'])
            manager._registered.append((
               attrs['__regexp__'], result,
            ))
        return result


class RemoteService(object):
    """Base remote service crawler"""
    __metaclass__ = BaseRemoteService

    def __init__(self, url):
        """Init remote service"""
        self._url = url
        self._description = NOT_STARTED

    def _parse(self):
        """Parse url"""
        raise NotImplementedError(self)

    def _match(self):
        """Get regexp match"""
        return self.regexp.match(self._url).groupdict()

    @property
    def description(self):
        """Transparent description"""
        if self._description == NOT_STARTED:
            try:
                self._description = self._parse()
            except Exception as e:
                self._description = None
                print e
        return self._description

    @property
    def regexp(self):
        """Transparent compiled regexp"""
        return re.compile(self.__regexp__)


class DummyRemoteService(RemoteService):
    """Dummy remote service crawler"""
    __default__ = True

    def _parse(self):
        """Parse url"""
        return None


class LastfmService(RemoteService):
    """Lastfm crawler"""
    __regexp__ = r'http(s*)://(www\.)*last(\.*)fm[^/]*/user/(?P<username>[^/]*)/*'

    def _parse(self):
        """Parse latfm page"""
        result = self._match()
        if not result or not result.get('username'):
            return None
        username = result['username']
        url = 'http://ws.audioscrobbler.com/1.0/user/%s/recenttracks.rss' % username
        tree = fromstring(urllib.urlopen(url).read())
        return tree.xpath('//item/title')[0].text
