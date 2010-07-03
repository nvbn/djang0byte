# -*- coding: utf-8 -*-
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from main.forms import LoginForm
from main.forms import RegisterForm
from main.models import *
    
def register(request, next = None):
    """Register new user"""
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
    """View user profile"""
    user = User.objects.filter(username=name)[0]
    profile = user.get_profile()
    return render_to_response('user.html', {'profile': profile, 'user': user})
    
@login_required
def myprofile(request):
    """View your own profile"""
    user = request.user
    profile = user.get_profile()
    return render_to_response('user.html', {'profile': profile, 'user': user})
    
def login(request, next = None):
    """Login user"""
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

def logout(request):
    """Getting out from here!"""
    auth.logout(request)
    return HttpResponseRedirect("/account/loggedout/")
# Create your views here.
