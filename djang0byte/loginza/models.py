import urllib
from django.contrib.auth.models import User
from django.core.files.uploadedfile import TemporaryUploadedFile
from django.db import models
from django.utils import simplejson as json
from functools import partial
from loginza import signals
from loginza.conf import settings
from main.models import Profile, Statused, MeOn

def make_username(username):
    counter = 1
    name = username
    while User.objects.filter(username=name).count():
        name += str(counter)
        counter += 1
    return username

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
                #username = loginza_nickname if loginza_nickname is not None else email.split('@')[0]
                username = email
                # check duplicate user name
                while True:
                    try:
                        existing_user = User.objects.get(username=username)
                        username = '%s%d' % (username, existing_user.id)
                    except User.DoesNotExist:
                        break
                add_meon = None
                filename = None
                if loginza_data['provider'] == 'http://twitter.com/':
                    username = loginza_data['nickname'] + '@twitter'
                    add_meon = partial(
                        Statused.objects.create,
                        title='twitter',
                        type=Statused.TYPE_TWITTER,
                        name=loginza_data['nickname'],
                        show=True,
                        url=loginza_data['identity']
                    )
                elif loginza_data['provider'] == 'http://www.facebook.com/':
                    username = loginza_data['email']
                    add_meon = partial(
                        MeOn.objects.create,
                        url=loginza_data['identity'],
                        title='facebook',
                    )
                elif loginza_data['provider'] == 'http://vkontakte.ru/':
                    name = loginza_data.get('name', {})
                    username = name.get('first_name', '') + ' ' + name.get('last_name', '')
                    if User.objects.filter(username=username).count():
                        username += '@vk.com'
                    add_meon = partial(
                        MeOn.objects.create,
                        url=loginza_data['identity'],
                        title='vkontakte',
                    )
                elif loginza_data['provider'] == 'http://openid.yandex.ru/server/':
                    username = loginza_data['identity'].split('/')[-2]
                    email = username + '@ya.ru'
                elif loginza_data['provider'] == 'http://www.last.fm/':
                    username = loginza_data['nickname'] + '@lastfm'
                    add_meon = partial(
                        Statused.objects.create,
                        title='lastfm',
                        type=Statused.TYPE_TWITTER,
                        name=loginza_data['nickname'],
                        show=True,
                        url=loginza_data['identity']
                    )
                    filename = unicode(loginza_data['nickname'] + '.jpg')
                if 'full_name' in loginza_data.get('name', {}):
                    if not User.objects.filter(username=loginza_data['name']['full_name']).count():
                        username = loginza_data['name']['full_name']
                if email == 'user@loginza':
                    email = 'set@your.email'
                user = User.objects.create_user(
                    make_username(username),
                    email
                )
                if add_meon:
                    add_meon(user=user)
                profile_kwargs = {
                    'user':user,
                }
                if 'default' in loginza_data.get('web', {}):
                    profile_kwargs['site'] = loginza_data['web']['default']
                if 'photo' in loginza_data:
                    f = urllib.urlopen(loginza_data['photo'])
                    file_data = f.read()
                    uploaded_file = TemporaryUploadedFile(
                        name=filename or unicode(username + '.jpg'),
                        content_type="image/jpeg",
                        size=len(file_data),
                        charset=None
                    )
                    uploaded_file.file.write(file_data)
                    profile_kwargs['avatar'] = uploaded_file
                Profile.objects.create(**profile_kwargs)
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
