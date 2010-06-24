from xml.dom.minidom import Comment
from djang0byte.main.forms import CreateCommentForm
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from main.forms import CreatePostForm, CreateCommentForm
from main.models import *

@login_required
def newpost(request):
    """Create post form and action"""
    profile = request.user.get_profile()
    if request.method == 'POST':
        form = CreatePostForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            post = Post()
            post.author = request.user
            post.blog = Blog.objects.filter(id=request.POST.get('blog'))[0]
            post.title = data['title']
            post.text = data['text']
            post.owner = request.user
            post.save()
            post.insertTags(data['tags'])
            return HttpResponseRedirect('/post/%d/' % (post.id))
    else:
        form = CreatePostForm()
    return render_to_response('newpost.html', {'form': form, 'blogs': profile.getBlogs()})

def post(request, id):
    """Print single post"""
    post = Post.objects.filter(id=id)[0]
    tags = post.getTags()
    author = post.author.get_profile()
    comments = post.getComment()
    
    return render_to_response('post.html', {'post': post, 'tags': tags, 
        'author': author, 'comments': comments})

def post_list(request, frm = 0, type = None, param = None):
    """Print post list"""
    if type == None:
        posts = Post.objects.all()[frm:][:10]
    elif type == 'blog':
        blog = Blog.objects.filter(id=param)[0]
        posts = blog.getPosts()[frm:][:10]
    elif type == 'tag':
        tag = Tag.objects.filter(name=param)[0]
        posts = tag.getPosts()[frm:][:10]
    elif type == 'auth':
        user = User.objects.filter(username=param)[0]
        profile = user.get_profile()
        posts = profile.getPosts()[frm:][:10]
        
    return render_to_response('post_list.html', {'posts': posts})

def post_list_with_param(request, type, param, frm = None):
    """Wrapper for post_list"""
    return post_list(request, frm, type, param)

@login_required
def new_comment(request, post = 0, comment = 0):
    """New comment form"""
    if request.method == 'POST':
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            comment = Comment()
            comment.post = Post.objects.filter(id=data['post'])[0]
            comment.root = data['comment']
            comment.author = request.user
            comment.text = data['text']
            comment.save()
            return HttpResponseRedirect('/post/%d/#cmnt%d' %
                            (comment.post.id, comment.id))
    else:
        form = CreateCommentForm({'post': post, 'comment': comment})
    return render_to_response('new_comment.html', {'form': form})