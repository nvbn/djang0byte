from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db import models
from tools.exceptions import (
    InvalidRateSignError, RateDisabledError,
    AlreadyRatedError, NotRemovedError,
    AlreadyRemovedError,
)
from tools.decorators import extend


RATE_MINUS = -1
RATE_PLUS = +1
RATES = (
    (RATE_MINUS, _('minus')),
    (RATE_PLUS, _('plus')),
)


class RateClassMixin(models.Model):
    """Mixin for rates models"""
    sign = models.PositiveSmallIntegerField(
        choices=RATES, verbose_name=_('sign'),
    )
    author = models.ForeignKey(User, verbose_name=_('author'))
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created'),
    )

    class Meta:
        abstract = True


def rateable_from(base=models.Model):
    """Create rateable mixin from"""
    class BaseRateableMixin(base):
        """Mixin for models with rates"""
        __rateclass__ = None

        rate = models.IntegerField(default=0, verbose_name=_('rate'))
        rate_count = models.IntegerField(default=0, verbose_name=_('rate'))
        is_rate_enabled = models.BooleanField(
            default=True, verbose_name=_('is rate enabled'),
        )

        def is_rated(self, user):
            """Check enemy is rated"""
            return bool(self.__rateclass__.objects.filter(
                author=user, enemy=self,
            ))

        def set_rate(self, sign, user):
            """Set rate"""
            if not self.is_rate_enabled:
                raise RateDisabledError(self)
            if self.is_rated(user):
                raise AlreadyRatedError(self)
            if sign in (RATE_PLUS, RATE_MINUS):
                self.rate = models.F('rate') + sign
                self.rate_count = models.F('rate_count') + 1
                self.__rateclass__.objects.create(
                    author=user, enemy=self, sign=sign,
                )
            else:
                raise InvalidRateSignError(self)

        class Meta:
            abstract = True
    return BaseRateableMixin


RateableMixin = rateable_from()


def removable_from(base=models.Model):
    """Create removable mixin from"""
    class BaseRemovableMixin(base):
        """Fake removable mixin"""
        is_removed = models.BooleanField(
            default=False, verbose_name=_('is removed'),
        )

        def remove(self):
            """Remove object"""
            if self.is_removed:
                raise AlreadyRemovedError(self)
            self.is_removed = True
            self.save()

        def restore(self):
            """Restore object"""
            if not self.is_removed:
                raise NotRemovedError(self)
            self.is_removed = False
            self.save()

        class Meta:
            abstract = True

    return BaseRemovableMixin


RmovableMixin = removable_from()
