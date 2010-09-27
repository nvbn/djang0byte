# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
from main.forms import CreateBlogForm, CreatePostForm
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from main.models import *

@login_required
def newblog(request):
    """Create blog form and action"""
    if request.method == 'POST':
        form = CreateBlogForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            blog = Blog()
            blog.name = data['name']
            blog.description = data['description']
            blog.owner = request.user
            blog.rate = 0
            blog.rate_count = 0
            blog.save()
            owner = UserInBlog()
            owner.blog = blog
            owner.user = request.user
            owner.save()
            return HttpResponseRedirect('/newpost/')
    else:
        form = CreateBlogForm()
    return render_to_response('newblog.html', {'form': form})
    
@login_required
def join(request, blog_id):
    """Join or withdraw from the blog"""
    blog = Blog.objects.get(id=blog_id)
    if blog.owner == request.user:
        pass
    if blog.checkUser(request.user):
        userInBlog = UserInBlog.objects.get(user=request.user, blog=blog)
        userInBlog.delete()
    else:
        userInBlog = UserInBlog()
        userInBlog.user = request.user
        userInBlog.blog = blog
        userInBlog.save()
    return HttpResponseRedirect('/blog/%d/' % (int(blog_id)))
