from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db import models
from tagging.fields import TagField
from tagging.models import Tag
from mptt.models import MPTTModel, TreeForeignKey
from tools.mixins import RateClassMixin, RateableMixin, rateable_from
from tools.decorators import extend
from blogging.exceptions import (
    AlreadySubscribedError, NotSubscribedError,
    AlreadyStarredError, NotStarredError,
    AlreadyAnsweredError, NotSeveralQuizError,
    AlreadyIgnoredError, VoteForIgnoredError,
    IgnoreForVotedError,
)


class BlogRate(RateClassMixin):
    """Rates for blog model"""
    enemy = models.ForeignKey('Blog', verbose_name=_('blog'))

    class Meta:
        verbose_name = _('BlogRate')
        verbose_name_plural = _('BlogRates')

    def __unicode__(self):
        return unicode(self.enemy)


class Blog(RateableMixin):
    """Blog model"""
    __rateclass__ = BlogRate

    name = models.CharField(max_length=300, verbose_name=_('name'))
    description = models.TextField(verbose_name=_('description'))
    author = models.ForeignKey(User, verbose_name=_('author'))

    class Meta:
        verbose_name = _('Blog')
        verbose_name_plural = _('Blogs')

    def __unicode__(self):
        return self.name


class PostRate(RateClassMixin):
    """Rates for post model"""
    enemy = models.ForeignKey('Post', verbose_name=_('post'))

    class Meta:
        verbose_name = _('PostRate')
        verbose_name_plural = _('PostRates')

    def __unicode__(self):
        return unicode(self.enemy)


class Post(RateableMixin):
    """Post model"""
    __rateclass__ = PostRate

    title = models.CharField(max_length=300, verbose_name=_('title'))
    preview = models.TextField(verbose_name=_('preview'))
    content = models.TextField(verbose_name=_('content'))
    blog = models.ForeignKey(Blog, null=True, verbose_name=_('blog'))
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

    def subscribe(self, user):
        """Subscribe user to post"""
        if self.is_subscribed(user):
            raise AlreadySubscribedError(self)
        user.subscriptions.add(self)

    def unsubscribe(self, user):
        """Unsubscribe user from post"""
        if not self.is_subscribed(user):
            raise NotSubscribedError(self)
        user.subscriptions.remove(self)

    def is_subscribed(self, user):
        """Check user is subscribed to post"""
        return bool(user.subscriptions.filter(id=self.id).count())

    def star(self, user):
        """Star user to post"""
        if self.is_starred(user):
            raise AlreadyStarredError(self)
        user.stars.add(self)

    def unstar(self, user):
        """Unstar user from post"""
        if not self.is_starred(user):
            raise NotStarredError(self)
        user.stars.remove(self)

    def is_starred(self, user):
        """Check user is starred to post"""
        return bool(user.stars.filter(id=self.id).count())


class Comment(rateable_from(MPTTModel)):
    """Comment models"""
    parent = TreeForeignKey(
        'self', null=True, blank=True,
        related_name='children', verbose_name=_('parent'),
    )
    author = models.ForeignKey(User, verbose_name=_('author'))
    content = models.TextField(verbose_name=_('content'))
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created'),
    )
    post = models.ForeignKey(Post, verbose_name=_('post'))


class Quiz(models.Model):
    """Quiz model"""
    name = models.CharField(max_length=300, verbose_name=_('name'))
    is_several = models.BooleanField(
        default=False, verbose_name=_('is several'),
    )
    ignorers = models.ManyToManyField(User, verbose_name=_('ignorers'))
    post = models.ForeignKey(Post, verbose_name=_('post'))

    def vote(self, user, answers):
        """Vote to answers"""
        if not hasattr(answers, '__iter__'):
            answers = [answers]
        if len(answers) > 1 and not self.is_several:
            raise NotSeveralQuizError(self)
        if self.is_voted(user):
            raise AlreadyAnsweredError(self)
        if self.is_ignored(user):
            raise VoteForIgnoredError(self)
        self.answers.filter(
            id__in=map(lambda answer: answer.id, answers),
        ).update(count=models.F('count') + 1)
        for answer in answers:
            answer.voters.add(user)

    def is_voted(self, user):
        """Check user is voted"""
        return bool(self.answers.filter(voters=user).count())

    def ignore(self, user):
        """ignore quiz"""
        if self.is_voted(user):
            raise IgnoreForVotedError(self)
        if self.is_ignored(user):
            raise AlreadyIgnoredError(self)
        self.ignorers.add(user)

    def is_ignored(self, user):
        """Check user is ignore quiz"""
        return bool(self.ignorers.filter(id=user.id).count())


class Answer(models.Model):
    """Answer for quiz model"""
    name = models.CharField(max_length=300, verbose_name=_('name'))
    count = models.PositiveIntegerField(
        default=0, verbose_name=_('count'),
    )
    quiz = models.ForeignKey(
        Quiz, related_name='answers', verbose_name=_('quiz'),
    )
    voters = models.ManyToManyField(User, verbose_name=_('voters'))


@extend(User)
class Profile(object):
    """Extended profile for blogging"""
    subscriptions = models.ManyToManyField(Post, 
        related_name='sub_users', verbose_name=_('subscriptions'),
    )
    stars = models.ManyToManyField(Post,
        related_name='star_users', verbose_name=_('stars'),
    )    
