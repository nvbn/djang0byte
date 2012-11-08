from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db import models
from tagging.fields import TagField
from tagging.models import Tag
from tools.mixins import RateableMixin


class Blog(models.Model, RateableMixin):
    name = models.CharField(max_length=300, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'))
    author = models.ForeignKey(User, verbose_name=_('author'))

    class Meta:
        verbose_name = _('Blog')
        verbose_name_plural = _('Blogs')

    def __unicode__(self):
        return self.name


class Post(models.Model, RateableMixin):
    title = models.CharField(max_length=300, verbose_name=_('title'))
    preview = models.TextField(verbose_name=_('preview'))
    content = models.TextField(verbose_name=_('content'))
    blog = models.ForeignKey(Blog, verbose_name=_('blog'))
    tags = TagField(blank=True, null=True, verbose_name=_('tags'))
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created'),
    )
    updated = models.DateTimeField(
        auto_now=True, verbose_name=_('updated'),
    )
    is_draft = models.BooleanField(
        default=False, verbose_name=_('is draft'),
    )
    is_attached = models.BooleanField(
        default=False, verbose_name=_('is attached'),
    )
    is_commenting_locked = models.BooleanField(
        default=False, verbose_name=_('is commenting locked'),
    )

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')

    def __unicode__(self):
        return self.title
    
