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


from main.forms import CreateBlogForm
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from main.models import *
from settings import DEFAULT_BLOG_TYPE
from annoying.decorators import render_to

@login_required
@render_to('newblog.html')
def newblog(request):
    """Create blog form and action

    Keyword arguments:
    request -- request object

    Returns: HttpResponse

    """
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
            blog.type = BlogType.objects.get(name=DEFAULT_BLOG_TYPE)
            blog.save()
            owner = UserInBlog()
            owner.blog = blog
            owner.user = request.user
            owner.save()
            return HttpResponseRedirect('/newpost/')
    else:
        form = CreateBlogForm()
    return({'form': form})
    
@login_required
def join(request, blog_id):
    """Join or withdraw from the blog

    Keyword arguments:
    request -- request object
    blog_id -- Integer

    Returns: HttpResponse

    """
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
