from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from annoying.decorators import ajax_request
from django.contrib.auth.views import logout_then_login
from django import http
from django.contrib import messages, auth
from django.shortcuts import redirect, render_to_response
from django.template.context import RequestContext
from loginza import signals, models
from loginza.models import UserMap
from loginza.templatetags.loginza_widget import _return_path
from main.models import Profile
from django.contrib.auth.views import login as original_login

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

def complete_loginza_registration(user_map, **kwargs):
    Profile.objects.create(
        user=user_map.user
    )

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
signals.created.connect(complete_loginza_registration)