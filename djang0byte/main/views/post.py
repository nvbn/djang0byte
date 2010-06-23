from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from main.forms import CreatePostForm
from main.models import *

@login_required
def newpost(request):
    """Create post form and action"""
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = CreatePostForm(request.POST, profile=profile)
        if form.is_valid():
            data = form.cleaned_data
            post = Post()
            post.blog = Blog.objects.filter(id=data['blog'])
            post.title = data['title']
            post.text = data['text']
            #post.tag = data['tag']
            post.owner = request.user
            post.save()
    else:
        form = CreatePostForm(profile=profile)
    return render_to_response('newpost.html', {'form': form})
