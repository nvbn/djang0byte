# -*- coding: utf-8 -*-
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.



from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from main.forms import LoginForm, RegisterForm, EditUserForm
from main.models import *
from django.db import transaction
from urlparse import urlparse

def register(request, next = None):
    """Register new user

    Keyword arguments:
    request -- request object
    next -- String

    Returns: HttpResponse

        """
    if next == None:
        if request.GET.get('next') == None:
            next = '/'
        else:
            next = request.GET.get('next')
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User()
            user.username = data['name']
            user.email = data['email']
            user.set_password(data['password'])
            user.save()
            profile = Profile()
            profile.user = user
            profile.save()
            return HttpResponseRedirect('/login/' + next)
    else:
        form = RegisterForm()
    return render_to_response('register.html', {'form': form, 'next': next})
    
def profile(request, name):
    """View user profile

    Keyword arguments:
    request -- request object
    name -- String

    Returns: HttpResponse

    """
    user = User.objects.filter(username=name)[0]
    profile = user.get_profile()
    meon = profile.get_me_on()
    for site in meon:
        parsed = urlparse(site['url'])
        site['favicon'] = 'http://' + unicode(parsed.netloc) + '/favicon.ico'
    return render_to_response('user.html', {'profile': profile, 'user': user,
                                            'mine': user == request.user, 'meon': meon})

    
def login(request, next = None):
    """Login user

    Keyword arguments:
    request -- request object
    next -- String

    Returns: HttpResponse

    """
    if next == None:
        if request.GET.get('next') == None:
            next = '/'
        else:
            next = request.GET.get('next')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = data['username']
            password = data['password']
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect(next)
    else:
        form = LoginForm()
    return render_to_response('login.html', {'form': form,
                              'next': next})
@login_required
def friend(request, name):
    """Add or remove friends

    Keyword arguments:
    request -- request object
    name -- String

    Returns: HttpResponse

    """
    user = User.objects.get(name=name)
    try:
        friend = Friends.objects.get(user=request.user,friend=user.id)
        friend.delete()
    except Friends.DoesNotExist:
        friend = Friends()
        friend.user = request.user
        friend.friend = user.id
        friend.save()
    
def logout(request):
    """Getting out from here!

    Keyword arguments:
    request -- request object

    Returns: HttpResponse

    """
    auth.logout(request)
    return HttpResponseRedirect("/")

@login_required
@transaction.commit_on_success
def edit_user(request):
    """Edit user data form

    Keyword arguments:
    request -- request object

    Returns: HttpResponse

    """
    if request.method == 'POST':
        form = EditUserForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            profile = request.user.get_profile()
            request.user.email = data['mail']
            profile.about = data['about']
            profile.icq = data['icq']
            profile.jabber = data['jabber']
            profile.timezone = data['timezone']
            profile.city = City.get_city(data['city'])
            profile.hide_mail = data['show_mail']
            profile.reply_comment = data['notify_comment_reply']
            profile.reply_pm = data['notify_pm']
            profile.reply_post = data['notify_post_reply']
            #profile.avatar = data['userpic']
            profile.site= data['site']
            profile.save()
            request.user.save()
            count = int(request.POST['count'])
            MeOn.objects.filter(user=request.user).delete()
            Statused.objects.filter(user=request.user).delete()
            for i in range(count):
                meon = MeOn()
                meon.url = request.POST['meon_url[%d]' % (i)]
                meon.title = request.POST['meon[%d]' % (i)]
                meon.user = request.user
                try:
                    meon.parse(request.POST['meon_status[%d]' % (i)])
                except:
                    meon.parse(False)
            return HttpResponseRedirect('/user/%s/' % (request.user))
    else:
        profile = request.user.get_profile()
        data = {'mail': request.user.email,
                'about': profile.about,
                'icq': profile.icq,
                'jabber': profile.jabber,
                'timezone': profile.timezone,
                'show_mail': profile.hide_mail,
                'notify_comment_reply': profile.reply_comment,
                'notify_post_reply': profile.reply_post,
                'notify_pm': profile.reply_pm,
                'city': profile.city,
                'site': profile.site,
        }
        form = EditUserForm(data)
    return render_to_response('edit_user.html', {'form': form, 'user': request.user, 'profile': request.user.get_profile()})

@login_required
@transaction.commit_on_success
def change_userpic(self):
    pass