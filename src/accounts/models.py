from django.utils.translation import ugettext as _
from django.db import models
from django.db.models.aggregates import Sum
from django.conf import settings
from django.contrib.auth.models import User
from tools.decorators import extend


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

    def update_rate(self):
        """Update user rate"""
        posts = self.post_set.aggregate(Sum('rate'))['rate__sum'] or 0
        comments = self.comment_set.aggregate(Sum('rate'))['rate__sum'] or 0
        blogs = self.blog_set.aggregate(Sum('rate'))['rate__sum'] or 0
        self.rate = POST_RATE * posts + COMMENT_RATE * comments + BLOG_RATE * blogs
        self.save()
