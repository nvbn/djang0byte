from itertools import imap, ifilter
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.db.utils import IntegrityError
from django.utils.translation import ugettext as _
from django.db import models
from datetime import datetime
import hashlib
from main.models import Profile, LastView, LentaLastView, LastVisit
from pytils import translit


class MergeKeyManager(models.Manager):
    def create(self, **kwargs):
        if not 'key' in kwargs and 'user' in kwargs:
            kwargs['key'] = MergeKey.generate_key(kwargs['user'])
        return super(MergeKeyManager, self).create(**kwargs)


class MergeKey(models.Model):
    """Users merge key"""
    user = models.ForeignKey(User, verbose_name=_('user'))
    key = models.CharField(
        max_length=32, editable=False, unique=True, verbose_name=_('key')
    )
    objects = MergeKeyManager()

    @staticmethod
    def generate_key(user):
        return hashlib.md5(
            "%d_%s" % (user.id, str(datetime.now()))
        ).hexdigest()

    def merge(self, new_user):
        LastView.objects.filter(user=self.user).delete()
        LastVisit.objects.filter(user=self.user).delete()
        LentaLastView.objects.filter(user=self.user).delete()
        profile = self.user.get_profile()
        new_profile = new_user.get_profile()
        models = ifilter(lambda model: model,
            imap(lambda ct: ct.model_class(), ContentType.objects.all())
        )
        for model in models:
            rels_vals = imap(lambda field: (field,
                (profile, new_profile) if field.rel.to is Profile else (self.user, new_user)),
                ifilter(lambda field:
                    getattr(field.rel, 'to', None) in (User, Profile),
                    model._meta.fields)
            )
            for field, (old_val, new_val) in rels_vals:
                for obj in model.objects.filter(**{
                    field.name: old_val
                }):
                    try:
                        setattr(obj, field.name, new_val)
                        obj.save()
                    except IntegrityError:
                        obj.delete()
#        for ct in ContentType.objects.all():
#            model = ct.model_class()
#            if model:
#                for field in model._meta.fields:
#                    if field.rel:
#                        _model = field.rel.to
#                        if _model == User:
#                            for obj in model.objects.filter(**{
#                                field.name: self.user
#                            }):
#                                try:
#                                    setattr(obj, field.name, new_user)
#                                    obj.save()
#                                except IntegrityError:
#                                    obj.delete()
#                        elif _model == Profile:
#                            for obj in model.objects.filter(**{
#                                field.name: self.user.get_profile()
#                            }):
#                                try:
#                                    setattr(obj, field.name, new_user.get_profile())
#                                    obj.save()
#                                except IntegrityError:
#                                    obj.delete()
        self.delete()
        self.user.delete()

    def save(self, *args, **kwargs):
        if not self.id and not self.key:
            self.key = MergeKey.generate_key(self.user)
        super(MergeKey, self).save(*args, **kwargs)
