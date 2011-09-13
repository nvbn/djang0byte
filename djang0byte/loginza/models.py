from django.contrib.auth.models import User
from django.db import models
from django.utils import simplejson as json

from loginza import signals
from loginza.conf import settings

class IdentityManager(models.Manager):
    def from_loginza_data(self, loginza_data):
        try:
            identity = self.get(identity=loginza_data['identity'])
            # update data as some apps can use it, e.g. avatars
            identity.data = json.dumps(loginza_data)
            identity.save()
        except self.model.DoesNotExist:
            identity = self.create(
                identity=loginza_data['identity'],
                provider=loginza_data['provider'],
                data=json.dumps(loginza_data)
            )
        return identity


class UserMapManager(models.Manager):
    def for_identity(self, identity, request):
        try:
            user_map = self.get(identity=identity)
        except self.model.DoesNotExist:
            # if there is authenticated user - map identity to that user
            # if not - create new user and mapping for him
            if request.user.is_authenticated():
                user = request.user
            else:
                loginza_data = json.loads(identity.data)

                loginza_email = loginza_data.get('email', '')
                email = loginza_email if '@' in loginza_email else settings.DEFAULT_EMAIL

                # if nickname is not set - try to get it from email
                # e.g. vgarvardt@gmail.com -> vgarvardt
                loginza_nickname = loginza_data.get('nickname', None)
                username = loginza_nickname if loginza_nickname is not None else email.split('@')[0]

                # check duplicate user name
                while True:
                    try:
                        existing_user = User.objects.get(username=username)
                        username = '%s%d' % (username, existing_user.id)
                    except User.DoesNotExist:
                        break

                user = User.objects.create_user(
                    username,
                    email
                )
            user_map = UserMap.objects.create(identity=identity, user=user)
            signals.created.send(request, user_map=user_map)
        return user_map


class Identity(models.Model):
    identity = models.CharField(max_length=255, unique=True)
    provider = models.CharField(max_length=255)
    data = models.TextField()

    objects = IdentityManager()

    def __unicode__(self):
        return self.identity

    class Meta:
        ordering = ['id']
        verbose_name_plural = "identities"


class UserMap(models.Model):
    identity = models.OneToOneField(Identity)
    user = models.ForeignKey(User)
    verified = models.BooleanField(default=False, db_index=True)

    objects = UserMapManager()

    def __unicode__(self):
        return '%s [%s]' % (unicode(self.user), self.identity.provider)

    class Meta:
        ordering = ['user']
