from django.utils.translation import ugettext as _
from django.db import models
from django.db.models.aggregates import Sum
from django.conf import settings
from django.contrib.auth.models import User
from annoying.fields import JSONField
from tools.decorators import extend
from accounts.remote_services import get_service


POST_RATE = getattr(settings, 'POST_RATE', 1.0)
BLOG_RATE = getattr(settings, 'BLOG_RATE', 0.7)
COMMENT_RATE = getattr(settings, 'COMMENT_RATE', 0.2)


class City(models.Model):  # maybe add lonlat?
    """City model"""
    name = models.CharField(
        unique=True, db_index=True,
        max_length=300, verbose_name=_('name'),
    )

    class Meta:
        verbose_name = _('City')
        verbose_name_plural = _('Citys')

    def __unicode__(self):
        return self.name


class RemoteServiceResult(object):
    """Remote service result abstraction"""
    def __init__(self, name, url):
        """Init with base datas"""
        self.name = name
        self.url = url
        self.description = get_service(url).description


@extend(User)
class Profile(object):
    """Extended user profile"""
    avatar = models.ImageField(
        upload_to='upload/%m/%d/',
        blank=True, null=True,
        verbose_name=_('avatar'),
    )
    jabber = models.EmailField(
        blank=True, null=True, verbose_name=_('jabber'),
    )
    site = models.URLField(
        blank=True, null=True, verbose_name=_('site'),
    )
    icq = models.CharField(
        max_length=15, blank=True, null=True,
        verbose_name=_('icq'),
    )
    about = models.TextField(verbose_name=_('about'))
    city = models.ForeignKey(
        City, blank=True, null=True, verbose_name=_('city'),
    )
    friends = models.ManyToManyField(
        User, related_name='frended', verbose_name=_('friends'),
    )
    rate = models.IntegerField(default=0, verbose_name=_('rate'))
    _services = JSONField(
        blank=True, null=True, verbose_name=_('remote services')
    )

    def update_rate(self):
        """Update user rate"""
        posts = self.post_set.aggregate(Sum('rate'))['rate__sum'] or 0
        comments = self.comment_set.aggregate(Sum('rate'))['rate__sum'] or 0
        blogs = self.blog_set.aggregate(Sum('rate'))['rate__sum'] or 0
        self.rate = POST_RATE * posts + COMMENT_RATE * comments + BLOG_RATE * blogs
        self.save()

    @property
    def services(self):
        """Transparent get services"""
        if not self._services:
            return []
        if not hasattr(self, '_cached_services'):
            self._cached_services = dict(map(
                lambda (name, url): (
                    name, RemoteServiceResult(name, url),
                ),
            self._services.items()))
        return self._cached_services

    @services.setter
    def services(self, urls):
        """Transparent get services"""
        self._services = urls
