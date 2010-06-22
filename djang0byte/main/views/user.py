from django.http import HttpResponse
from django.shortcuts import render_to_response
from main.forms import RegisterForm
from main.forms import LoginForm
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from main.models.profile import Profile

    
def register(request):
    """Register new user"""
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User()
            user.name = data['name']
            user.email = data['email']
            user.password = data['password']
    else:
        form = RegisterForm()
    return render_to_response('register.html', {'form': form})
    
def profile(request, name):
    """View user profile"""
    user = User.objects.filter(username = name)[0]
    profile = Profile.objects.filter(user = user)
    return render_to_response('user.html', {'profile': profile, 'user': user})
    
@login_required
def myprofile(request):
    """View your own profile"""
    user = request.user
    profile = Profile.objects.filter(user = user)
    return render_to_response('user.html', {'profile': profile, 'user': user})
    
def login(request):
    """Login user"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = auth.authenticate(username=username, password=password)
            if user is not None and user.is_active:
                auth.login(request, user)
                return HttpResponseRedirect("/user/")
    else:
        form = LoginForm()
        
    return render_to_response('login.html', {'form' : form})

def logout(request):
    """Getting out from here!"""
    auth.logout(request)
    return HttpResponseRedirect("/account/loggedout/")
# Create your views here.
