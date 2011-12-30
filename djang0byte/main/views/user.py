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
from django.shortcuts import render_to_response, get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.cache import never_cache
from loginza.models import UserMap
from main.forms import LoginForm, RegisterForm, EditUserForm, EditUserPick, EditUserPick
from main.models import *
from django.db import transaction
from urlparse import urlparse
from django.template.context import RequestContext
from annoying.decorators import render_to
from simplepagination import paginate
from djang0parser.utils import parse
from random import random

@render_to('register.html')
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
    return {
        'form': form,
        'next': next
    }
    
@render_to('user.html')
def profile(request, name):
    """View user profile

    Keyword arguments:
    request -- request object
    name -- String

    Returns: HttpResponse

    """
    user =get_object_or_404(User, username=name)
    profile = user.get_profile()
    meon = profile.get_me_on()
    for (id, site) in enumerate(meon):
        try:
            parsed = urlparse(site['url'])
            site['favicon'] = 'http://' + unicode(parsed.netloc) + '/favicon.ico'
        except TypeError:
            meon.pop(id)
    return {
        'profile_user': profile,
        'user_user': user,
        'is_my_friend': profile.is_my_friend(request.user),
        'mine': user == request.user,
        'meon': meon,
        'is_social': UserMap.objects.filter(user=profile.user).count(),
    }


@render_to('login.html')
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
    return {
        'form': form,
        'next': next
    }

@never_cache
@login_required
def friend(request, name):
    """Add or remove friends

    Keyword arguments:
    request -- request object
    name -- String

    Returns: HttpResponse

    """
    user = get_object_or_404(User, username=name)
    if name != request.user.username:
        try:
            friend = Friends.objects.get(user=request.user.get_profile(),friend=user)
            friend.delete()
        except Friends.DoesNotExist:
            friend = Friends()
            friend.user = request.user.get_profile()
            friend.friend = user
            friend.save()
    return HttpResponseRedirect('/user/%s/' % (name))
    
def logout(request):
    """Getting out from here!

    Keyword arguments:
    request -- request object

    Returns: HttpResponse

    """
    auth.logout(request)
    return HttpResponseRedirect("/")

@never_cache
@login_required
@render_to('edit_user.html')
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
            profile.about = parse(data['about'])
            profile.icq = data['icq']
            profile.jabber = data['jabber']
            profile.timezone = data['timezone']
            if data['city']:
                profile.city = City.get_city(data['city'])
            profile.hide_mail = data['show_mail']
            profile.reply_comment = data['notify_comment_reply']
            profile.reply_pm = data['notify_pm']
            profile.reply_post = data['notify_post_reply']
            profile.reply_mention = data['notify_mention']
            profile.reply_spy = data['notify_spy']
            #profile.avatar = data['userpic']
            profile.site= data['site']
            profile.save()
            request.user.save()
            count = int(request.POST['count'])
            MeOn.objects.filter(user=request.user).delete()
            Statused.objects.filter(user=request.user).delete()
            for i in range(count):
                try:
                    meon = MeOn()
                    meon.url = request.POST['meon_url[%d]' % (i)]
                    meon.title = request.POST['meon[%d]' % (i)]
                    meon.user = request.user
                    try:
                        meon.parse(request.POST['meon_status[%d]' % (i)])
                    except:
                        meon.parse(False)
                    print meon.user
                except MultiValueDictKeyError:
                    pass
            return HttpResponseRedirect('/user/%s/' % (request.user.username,))
    else:
        profile = request.user.get_profile()
        data = {
            'mail': request.user.email,
            'about': profile.about,
            'icq': profile.icq,
            'jabber': profile.jabber,
            'timezone': profile.timezone,
            'show_mail': profile.hide_mail,
            'notify_comment_reply': profile.reply_comment,
            'notify_post_reply': profile.reply_post,
            'notify_pm': profile.reply_pm,
            'notify_mention': profile.reply_mention,
            'notify_spy': profile.reply_spy,
            'city': profile.city,
            'site': profile.site,
        }
        form = EditUserForm(data)
    return {
        'form': form,
        'user': request.user,
        'profile': request.user.get_profile()
    }

@never_cache
@login_required
@render_to('change_userpic.html')
@transaction.commit_on_success
def change_userpic(request):
    """Chage user picture

    Keyword arguments:
    request -- request object

    Returns: HttpResponse

    """
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = EditUserPick(request.POST, request.FILES)
        if form.is_valid():
            data = form.cleaned_data
            profile.avatar = data['userpic']
            profile.save()
        return HttpResponseRedirect('/user/%s/?%d' % (
            request.user,
            int(random()*999))
        )
    else:
        form = EditUserPick()
    return {
        'form': form,
        'profile': profile
    }

@never_cache
@login_required
@transaction.commit_on_success
def delete_userpic(request):
    """Delete user picture

    Keyword arguments:
    request -- request object

    Returns: HttpResponse

    """
    profile = request.user.get_profile()
    profile.avatar = None
    profile.save()
    return HttpResponseRedirect('/user/%s/?%d' % (
        request.user,
        int(random()*999))
    )

@render_to("user_comments.html")
@paginate(style='digg', per_page=50)
def comments(request, user):
    """Show user comments

    Keyword arguments:
    request -- request object
    user -- Unicode

    Returns: HttpResponse

    """
    user = get_object_or_404(User, username=user)
    comments = Comment.objects.filter(author=user).order_by('-created')
    return {
        'user': user,
        'object_list': comments,
        'profile': user.get_profile()
    }
