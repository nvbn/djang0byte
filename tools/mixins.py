from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.db import models
from tools.exceptions import InvalidRateSignError, RateDisabledError


RATE_MINUS = -1
RATE_PLUS = +1
RATES = (
    (RATE_MINUS, _('minus')),
    (RATE_PLUS, _('plus')),
)


class RateClassMixin(object):

    sign = models.PositiveSmallIntegerField(
        choices=RATES, verbose_name=_(RATES),
    )
    author = models.ForeignKey(User, verbose_name=_('author'))
    created = models.DateTimeField(
        auto_now_add=True, verbose_name=_('created'),
    )


class RateableBase(models.base.ModelBase):
    def __new__(cls, name, bases, attrs):
        if not 'rate_class' in attrs:
            attrs['rate_class'] = type('%sRate' % cls.__name__, (
                models.Model, RateableMixin,
            ), {
                'enemy': models.ForeignKey(cls, verbose_name=_('enemy')),
            })
        return super(RateableBase, cls).__new__(cls, name, bases, attrs)


class RateableMixin(object):
    __metaclass__ = RateableBase

    rate = models.IntegerField(default=0, verbose_name=_('rate'))
    rate_count = models.IntegerField(default=0, verbose_name=_('rate'))
    is_rate_enabled = models.BooleanField(
        default=True, verbose_name=_('is rate enabled'),
    )

    def is_rated(self, user):
        return bool(self.rate_class.objects.filter(
            author=user, enemy=self,
        ))

    def set_rate(self, sign):
        if not is_rate_enabled:
            raise RateDisabledError(self)
        if sign in (RATE_PLUS, RATE_MINUS):
            self.rate = models.F('rate') + sign
            self.rate_count = models.F('rate_count') + 1
        else:
            raise InvalidRateSignError(self)
