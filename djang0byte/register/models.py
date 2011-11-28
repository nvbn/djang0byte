from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext as _
from django.db import models
from datetime import datetime
import hashlib
from main.models import Profile


class MergeKeyManager(models.Manager):
    def create(self, **kwargs):
        if not 'key' in kwargs and 'user' in kwargs:
            kwargs['key'] = MergeKey.generate_key(kwargs['user'])
        super(MergeKeyManager, self).create(**kwargs)


class MergeKey(models.Model):
    """Users merge key"""
    user = models.ForeignKey(User, verbose_name=_('user'))
    key = models.CharField(
        max_length=32, editable=False, unique=True, verbose_name=_('key')
    )
    objects = MergeKeyManager

    @staticmethod
    def generate_key(user):
        return hashlib.md5(
            "%d_%s_%s" % (user.id, user.username, str(datetime.now()))
        ).hexdigest()

    def merge(self, new_user):
        for ct in ContentType.objects.all():
            model = ct.model_class()
            for field, _model in model._meta.get_fields_with_model().items():
                if _model == User:
                    model.objects.filter(**{
                        field.name: self.user
                    }).update(**{
                        field.name: new_user
                    })
                elif _model == Profile:
                    model.objects.filter(**{
                        field.name: self.user.get_profile()
                    }).update(**{
                        field.name: new_user.get_profile()
                    })
        self.delete()
        self.user.delete()

    def save(self, *args, **kwargs):
        if not self.id and not self.key:
            self.key = MergeKey.generate_key(self.user)
        super(MergeKey, self).save(*args, **kwargs)
