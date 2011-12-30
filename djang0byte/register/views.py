from main.models import Profile
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from annoying.decorators import ajax_request, render_to
from django.contrib.auth.views import logout_then_login
from django.contrib import auth
from django.shortcuts import redirect, get_object_or_404
from loginza import signals, models
from loginza.models import UserMap
from django.contrib.auth.views import login as original_login
from register.models import MergeKey
from sendmail.models import Mails
from django.utils.translation import ugettext as _

@ajax_request
def check(request, type, value, value_2 = None):
    if type == 'mail':
        try:
            User.objects.get(email=value)
            return {
                'value': False,
                'type': type
            }
        except User.DoesNotExist:
            return {
                'value': True,
                'type': type
            }
    elif type == 'username':
        try:
            User.objects.get(username=value)
            return {
                'value': False,
                'type': type
            }
        except User.DoesNotExist:
            return {
                'value': True,
                'type': type
            }
    elif type == 'all':
        try:
            User.objects.get(email=value_2)
            mail = False
        except User.DoesNotExist:
            mail = True
        try:
            User.objects.get(username=value)
            username = False
        except User.DoesNotExist:
            username = True
        return {
            'username': username,
            'mail': mail
        }

@login_required
def logout(request):
    return logout_then_login(request,'/')

@login_required
@ajax_request
def generate_merge_key(request):
    key = MergeKey.objects.create(
        user=request.user,
    )
    Mails.objects.create(
        subject=_('You try to merge accounts'),
        message=_('For merging account %(username)s with another go to this %(url)s,' \
                  ' for merging you need to login to main user' % {
            'username': request.user.username,
            'url': getattr(settings, 'SITE_URL') + '/merge_accounts/?key=' + key.key,
        }),
        recipient=request.user,
    )
    return {
        'status': True,
    }

@login_required
@render_to('registration/merge.html')
def merge(request):
    key = get_object_or_404(
        MergeKey,
        key=request.GET.get('key', None),
    )
    if key.user == request.user:
        return {
            'relogin': True
        }
    try:
        key.merge(request.user)
        return {
            'success': True
        }
    except (User.DoesNotExist, Profile.DoesNotExist):
        return {
            'error': True
        }

def loginza_auth_handler(sender, user, identity, **kwargs):
    try:
        user_map = UserMap.objects.get(user=user)
        auth.login(sender, user)
        return redirect(sender.session.get('_next', '/'))
    except models.UserMap.DoesNotExist:
        #sender.session['users_complete_reg_id'] = identity.id
        pass

def login(request, *args, **kwargs):
    request.session['_next'] = request.GET.get('next')
    return original_login(request, *args, **kwargs)

signals.authenticated.connect(loginza_auth_handler)