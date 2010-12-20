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



from django.db import transaction
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from main.forms import *
from main.models import *
from django.views.decorators.cache import cache_page
from simplepagination import paginate
from annoying.decorators import render_to
from tagging.models import TaggedItem
from main.utils import Access
from django.template import RequestContext
from settings import DEFAULT_CACHE_TIME
from django.views.decorators.vary import vary_on_cookie
from django.utils import simplejson
from django.utils.translation import gettext as _


@transaction.commit_on_success
@login_required
def newpost(request, type = 'post'):
    """Create post form and action

    Keyword arguments:
    request -- request object
    type -- String

    Returns: HttpResponse

    """
    profile = request.user.get_profile()
    type = request.GET.get('type') or 'post'
    extend = 'base.html'
    if request.GET.get('json'):
        extend = 'json.html'
    if type != 'answer':
      if request.method == 'POST':
          form = CreatePostForm(request.POST)
          if form.is_valid():
              data = form.cleaned_data
              post = Post()
              post.author = request.user
              post.set_blog(request.POST.get('blog'))
              post.title = data['title']
              post.text = data['text']
              post.owner = request.user
              post.type = 0#'Post'
              post.save()
              post.set_tags(data['tags'])
              post.create_comment_root()
              Notify.new_post_notify(post)
              #comment_root = Comment.add_root(post=post, created=datetime.datetime.now())
              #comment_root.save()
              return HttpResponseRedirect('/post/%d/' % (post.id))
      else:
           if type == 'post':
             form = CreatePostForm()
           elif type == 'link':
             form = CreatePostLinkForm()
           elif type == 'translate':
             form = CreatePostTranslateForm()
           blogs = [uib.blog for uib in profile.get_blogs()]
           blogs += Blog.objects.filter(default=True)
           d = {}
           for x in blogs:
                d[x]=x
           blogs = d.values()
           return render_to_response('newpost.html',
                                     {'form': form, 'blogs': blogs, 'type': type, 'extend': extend},
                                     context_instance=RequestContext(request))
    else:
      if request.method == 'POST':
        post = Post()
        post.title = request.POST.get('title')
        post.author = request.user
        post.set_blog(request.POST.get('blog'))
        if request.POST.get('multi', 0):
          post.type = 4#'Multiple Answer'
        else:
          post.type = 3#post.type = 'Answer'
        post.save()
        post.set_tags(request.POST.get('tags'))
        post.create_comment_root()
        for answer_item in range(int(request.POST.get('count'))):
          answer = Answer()
          answer.value = request.POST.get(str(answer_item))
          answer.post = post
          answer.save()
        return HttpResponseRedirect('/post/%d/' % (post.id))
      multi = False
      count = 2
      return render_to_response('newanswer.html', {'answers_count': range(count),
      'count': count, 'blogs': profile.get_blogs(), 'multi': multi, 'extend': extend},
                                context_instance=RequestContext(request))

@cache_page(DEFAULT_CACHE_TIME)
@render_to('post.html')
def post(request, id):
    """Print single post

    Keyword arguments:
    request -- request object
    id -- Integer

    Returns: HttpResponse

    """
    post = Post.objects.get(id=id)
    author = post.author.get_profile()
    comments = post.get_comment()
    form = CreateCommentForm({'post': id, 'comment': 0})
    post.get_content = post.get_full_content
    post.is_answer(request.user)
    return({'post': post, 'author': author, 'comments': comments, 'comment_form': form,
        'single': True})


@cache_page(DEFAULT_CACHE_TIME)
@render_to('post_list.html')
@paginate(style='digg', per_page=10)
def post_list(request, type = None, param = None):
    """Print post list

    Keyword arguments:
    request -- request object
    type -- String
    param -- String

    Returns: Array

    """
    posts = None
    subject = None
    option = None
    if type == None:
        blog_types = BlogType.objects.filter(display_default=False)
        blogs = Blog.objects.filter(type__in=blog_types)
        posts = Post.objects.exclude(blog__in=blogs)
    elif BlogType.check(type):
        posts = Post.objects.filter(blog__in=BlogType.objects.get(name=type).getBlogs())
    elif type == 'pers':
        posts = Post.objects.filter(blog=None)
    elif type == 'blog':
        blog = Blog.objects.get(id=param)
        posts = blog.get_posts()
        subject = blog
        option = blog.check_user(request.user)
    elif type == 'tag':
        posts = TaggedItem.objects.get_by_model(Post, param)
        subject = param
        #posts = [post.post for post in posts_with_tag]
    elif type == 'auth':
        user = User.objects.get(username=param)
        profile = user.get_profile()
        posts = profile.get_posts()
        subject = profile
        option = profile.is_my_friend(request.user)
    elif type == 'favourite':
        favourites = Favourite.objects.filter(user=request.user)
        posts = [post.post for post in favourites]
    posts = posts.order_by('-id')
    return {'object_list': posts, 'single': False, 'type': type, 'subject': subject, 'option': option}

def post_list_with_param(request, type, param = None):
    """Wrapper for post_list

    Keyword arguments:
    request -- request object
    type -- String
    param -- String

    Returns: HttpResponse

    """
    return post_list(request, type, param)

@login_required
def new_comment(request, post = 0, comment = 0):
    """New comment form

    Keyword arguments:
    request -- request object
    post -- Integer
    comment -- Integer

    Returns: HttpResponse

    """
    extend = 'base.html'
    json = False
    if request.GET.get('json', 0):
        extend = 'json.html'
        json = True
    print request.GET.get('json')
    if request.method == 'POST':
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            post = Post.objects.get(id=data['post'])
            if data['comment'] == 0:
                root = Comment.objects.get(post=post, depth=1)
            else:
                root = Comment.objects.get(id=data['comment'])

            comment = root.add_child(post=post,
            author=request.user, text=data['text'],
            created=datetime.datetime.now())
            comment.save()
            Notify.new_comment_notify(comment)
            if json:
                return(render_to_response('comment.html',
                                          {'post': comment.post, 'comment': comment, 'extend': extend},
                                          context_instance=RequestContext(request)))
            else:
                return HttpResponseRedirect('/post/%d/#cmnt%d' %
                            (comment.post.id, comment.id))
    else:
        form = CreateCommentForm({'post': post, 'comment': comment})
    return render_to_response('new_comment.html', {'form': form, 'extend': extend, 'pid': post, 'cid': comment},
                              context_instance=RequestContext(request))


@login_required
def action(request, type, id, action = None):
    """Add or remove from favourite and spy, rate

    Keyword arguments:
    request -- request object
    type -- String
    id -- Integer
    action -- String

    Returns: Array

    """
    json = False
    if request.GET.get('json', 0):
        extend = 'json.html'
        json = True
    jsend = lambda data: HttpResponse(simplejson.dumps(data), mimetype='application/json')
    try:
        post = Post.objects.select_related('author').get(id=id)
    except Post.DoesNotExist:
        post = Post()
    profile = Profile.objects.get(user=request.user)
    if type == 'inblog':
        blog = Blog.objects.get(id=id)
        blog.addOrRemoveUser(request.user)
        return HttpResponseRedirect('/blog/%d/' % (int(id)))
    elif type == 'ratecom':
        comment = Comment.objects.select_related('post').get(id=id)
        if request.user != comment.author:
            if profile.check_access(Access.rateComment):
                if action == '1':
                  rate = comment.rate_comment(request.user, +1)
                elif action == '0':
                  rate = comment.rate_comment(request.user, -1)
                error = ''
                if not rate:
                    error = _('Second vote is forbidden!')
                if json:
                    return jsend({'error': error, 'rate': comment.rate, 'id': comment.id })
                else:
                    return HttpResponseRedirect('/post/%d/#cmnt%d' % (comment.post.id, int(id)))
            else:
                return jsend({'error': _('Not allow this action!')})
        elif json:
            return jsend({'error': _('For their comments can not vote!')})
    elif type == 'rateblog' and request.user != post.author and profile.checkAccess(Access.rateBlog):
        blog = Blog.objects.get(id=id)
        if action == '1':
          blog.rateBlog(request.user, +1)
        elif action == '0':
          blog.rateBlog(request.user, -1)
        return HttpResponseRedirect('/blog/%d/' % (int(id)))


    post = Post.objects.get(id=id)
    if type == 'favourite':
        try:
            favourite = Favourite.objects.get(post=post, user=request.user)
            favourite.delete()
        except Favourite.DoesNotExist:
            favourite = Favourite()
            favourite.post = post
            favourite.user = request.user
            favourite.save()
    elif type == 'spy':
        spy = Spy.object.get(post=post, user=request.user)
        if spy:
            spy.delete()
        else:
            spy.post = post
            spy.user = request.user
            spy.save()
    elif type == 'ratepost' and request.user != post.author and profile.checkAccess(Access.ratePost):
        if action == '1':
          post.ratePost(request.user, +1)
        elif action == '0':
          post.ratePost(request.user, -1)
    elif type == 'answer':
        answers = Answer.objects.filter(post=post)
        if post.type == 3:
            answers.get(id=request.POST.get('answ')).vote(request.user)
        elif post.type == 4:
            for answer in answers:
                if request.POST.get('answ_' + str(answer.id), 0):
                    answer.vote(request.user, True)
            answer.fix(request.user)

    return HttpResponseRedirect('/post/%d/' % (int(id)))


@cache_page(DEFAULT_CACHE_TIME)
@vary_on_cookie
@login_required
@render_to('lenta.html')
@paginate(style='digg', per_page=10)
def lenta(request):
    """Return last posts and comments, adresed to user

    Keyword arguments:
    request -- request object

    Returns: Array

    """
    notifs = Notify.objects.select_related('post', 'comment').filter(user=request.user)
    return {'object_list': notifs}

