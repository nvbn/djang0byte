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
from main.forms import LoginForm
from main.forms import RegisterForm
from main.models import *
    
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
    return render_to_response('user.html', {'profile': profile, 'user': user})
    
@login_required
def myprofile(request):
    """View your own profile

    Keyword arguments:
    request -- request object

    Returns: HttpResponse

    """
    user = request.user
    profile = user.get_profile()
    return render_to_response('user.html', {'profile': profile, 'user': user})
    
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

