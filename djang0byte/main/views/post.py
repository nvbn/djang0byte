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
from django.core.exceptions import MultipleObjectsReturned
from itertools import imap
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response, get_object_or_404
from main.forms import *
from main.models import *
from django.views.decorators.cache import cache_page, never_cache
from simplepagination import paginate
from annoying.decorators import render_to
from tagging.models import TaggedItem
from django.template import RequestContext
from actions import  get_last_comments
from settings import DEFAULT_CACHE_TIME, POST_RATE_TO_MAIN, FULLNAME, FEED_URL
from django.views.decorators.vary import vary_on_cookie
from django.utils.translation import ugettext as _
from haystack.query import SearchQuerySet
from xapian_backend import InvalidIndexError

@never_cache
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
    preview = False
    is_draft = False
    if request.POST.get('draft'):
        is_draft = True
    if request.POST.get('preview'):
        preview = True
        is_draft = True

    extend = 'base.html'
    if request.GET.get('json'):
        extend = 'json.html'
    if type != 'answer':
        _type = type
        if type == 'post':
            type = Post.TYPE_POST
            form = CreatePostForm
        elif type == 'link':
            type = Post.TYPE_LINK
            form = CreatePostLinkForm
        else:
            type = Post.TYPE_TRANSLATE
            form = CreatePostTranslateForm
        if request.method == 'POST':
            form = form(request.POST)
            if form.is_valid() and not (preview or is_draft):
                data = form.cleaned_data
                post = Post()
                post.author = request.user
                post.type = type
                post.set_data(data)
                post.save(edit=False, retry=True)
                post.create_comment_root()
                post.set_tags(data['tags'])
                for mention in utils.find_mentions(data['text']):
                    Notify.new_mention_notify(mention, post=post)
                return HttpResponseRedirect('/post/%d/' % (post.id))
            else:
                if is_draft:
                    draft = Draft()
                    draft.author = request.user
                    draft.set_data(form.data)
                    draft.type = type
                    draft.save(edit=False)
                    if preview:
                        return HttpResponseRedirect('/draft/%d/' % (draft.id))
                    else:
                        return HttpResponseRedirect('/draft/')
                return render_to_response('newpost.html', {
                        'form': form,
                        'blogs': Blog.create_list(profile),
                        'type': _type,
                        'extend': extend
                    }, context_instance=RequestContext(request))
        else:
            return render_to_response('newpost.html', {
                'form': form(),
                'blogs': Blog.create_list(profile),
                'type': _type,
                'extend': extend
            }, context_instance=RequestContext(request))
    else:
        if request.method == 'POST':
            post = Post()
            post.title = request.POST.get('title')
            post.author = request.user
            post.set_blog(request.POST.get('blog'))
            if request.POST.get('multi', 0):
                post.type = Post.TYPE_MULTIPLE_ANSWER
            else:
                post.type = Post.TYPE_ANSWER
            post.save(edit=False)
            post.create_comment_root()
            post.set_tags(request.POST.get('tags'))
            for answer_item in range(int(request.POST.get('count'))):
                answer = Answer()
                answer.value = request.POST.get(str(answer_item))
                answer.post = post
                answer.save()
            return HttpResponseRedirect('/post/%d/' % (post.id))
        multi = False
        count = 2
        return render_to_response('newanswer.html', {
            'answers_count': range(count),
            'count': count,
            'blogs': Blog.create_list(profile),
            'multi': multi, 'extend': extend
        }, context_instance=RequestContext(request))

@cache_page(DEFAULT_CACHE_TIME)
@render_to('post.html')
def post(request, id):
    """Print single post

    Keyword arguments:
    request -- request object
    id -- Integer

    Returns: HttpResponse

    """
    post = get_object_or_404(Post, id=id)
    author = post.author.get_profile()
    comments = post.get_comment()
    form = CreateCommentForm({'post': id, 'comment': 0})
    post.get_content = post.get_full_content
    post.is_answer(request.user)
    options = {}
    last_view_date = None
    if request.user.is_authenticated():
        try:
            try:
                options['favourite'] = Favourite.objects.get(post=post, user=request.user)
            except Favourite.DoesNotExist:
                options['favourite'] = False
        except MultipleObjectsReturned:
            Favourite.objects.filter(post=post, user=request.user).delete()
            options['favourite'] = False
        try:
            try:
                options['spy'] = Spy.objects.get(post=post, user=request.user)
            except Spy.DoesNotExist:
                options['spy'] = False
        except MultipleObjectsReturned:
            Spy.objects.filter(post=post, user=request.user).delete() #shit, but work
            options['spy'] = False
        try:
            last_view = LastView.objects.get(post=post, user=request.user)
            last_view_date = last_view.date
            last_view.update()
        except:
            last_view = LastView(post=post, user=request.user)
            last_view_date = 1
            last_view.save()
    return({
        'post': post,
        'author': author,
        'comments': comments,
        'comment_form': form,
        "options": options,
        'single': True,
        'PERM_EDIT_POST': post.type < 3 and (
            request.user.has_perm('main.change_post') or request.user == post.author
        ),
        'last_view': last_view_date,
        'is_qa': post.blog.type.is_qa if post.blog is not None else False,
        'right_answer': post.right_answer,
    })


@cache_page(DEFAULT_CACHE_TIME)
@render_to('post_list.html')
@paginate(style='digg', per_page=10)
def post_list(request, post_type = None, param = None):
    """Print post list

    Keyword arguments:
    request -- request object
    post_type -- String
    param -- String

    Returns: Array

    """
    posts = None
    subject = None
    option = None
    rss = FEED_URL
    is_qa = False
    if not post_type:
        title = FULLNAME
        blog_types = BlogType.objects.filter(display_default=False)
        blogs = Blog.objects.filter(type__in=blog_types)
        posts = Post.objects.exclude(blog__in=blogs).filter(rate__gt=POST_RATE_TO_MAIN)
    elif BlogType.check(post_type):
        blog_type = BlogType.objects.get(name=post_type)
        is_qa = blog_type.is_qa
        title = blog_type.name
        posts = Post.objects.filter(blog__in=blog_type.get_blogs())
        if param == 'solved':
            posts = posts.filter(solved=True)
        elif param == 'unsolved':
            posts = posts.filter(solved=False)
        rss = '/rss/%s/' % (post_type)
    elif post_type == 'pers':
        title = _('Presonal posts')
        posts = Post.objects.filter(blog=None)
    elif post_type == 'blog':
        blog = Blog.objects.get(id=param)
        title = _('Blog in %s') % blog.name
        posts = blog.get_posts()
        subject = blog
        option = request.user.is_authenticated() and blog.check_user(request.user)
        rss = '/rss/blog/%s/' % (param)
    elif post_type == 'tag':
        title = _(u'Posts with tag %s') % unicode(param)
        posts = TaggedItem.objects.get_by_model(Post, param)
        subject = param
        rss = '/rss/tag/%s/' % (param)
        #posts = [post.post for post in posts_with_tag]
    elif post_type == 'auth':
        title = _('Posts by %s') % param
        user = User.objects.get(username=param)
        profile = user.get_profile()
        posts = profile.get_posts()
        subject = profile
        option = request.user.is_authenticated() and profile.is_my_friend(request.user)
        rss = '/rss/auth/%s/' % (param)
    elif post_type == 'like':
        post = Post.objects.get(id=param)
        posts = TaggedItem.objects.get_related(post, Post)
        title = _(u'Posts like %s') % (post.title)
        subject = post
    elif post_type == 'favourite':
        title = _('Favourite posts')
        #TODO: rewrite favorite to ManyToMany
        posts = Post.objects.filter(favourite__user=request.user)
    else:
        # Do not crash on unknown type
        raise Http404(_('Address not found: %s') % post_type)
    if posts and type(posts) not in (imap, list):
        posts = posts.order_by('-pinch', '-id').select_related('author', 'blog', 'author__profile')
    #TODO: fix answer result in post list
    return {
        'object_list': posts,
        'single': False,
        'post_type': post_type,
        'subject': subject,
        'option': option,
        'title': title,
        'rss': rss,
        'is_qa': is_qa,
        'param': param,
    }

def post_list_with_param(request, post_type, param = None):
    """Wrapper for post_list

    Keyword arguments:
    request -- request object
    post_type -- String
    param -- String

    Returns: HttpResponse

    """
    return post_list(request, post_type, param)

@never_cache
@login_required
def new_comment(request, post=0, comment=0):
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
    if request.method == 'POST':
        form = CreateCommentForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            comment = data['root'].add_child(
                post=data['post_obj'],
                author=request.user,
                text=data['text'],
                created=datetime.datetime.now()
            )
            comment.save()
            if request.user not in (data['root'].author, comment.post.author):
                Notify.new_comment_notify(comment)
            for mention in utils.find_mentions(data['raw_text']):
                Notify.new_mention_notify(mention, comment=comment)
            if json:
                return get_last_comments(request, comment.post.id, comment.id)
            else:
                return HttpResponseRedirect('/post/%d/#cmnt%d' %
                            (comment.post.id, comment.id))
    else:
        form = CreateCommentForm({
            'post': post,
            'comment': comment
        })
    return render_to_response('new_comment.html', {
        'form': form,
        'extend': extend,
        'pid': post,
        'cid': comment,
        'json': json
    }, context_instance=RequestContext(request))


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
    notifs = Notify.objects.select_related(
        'post', 'comment', 'post__author', 'comment__author',
        'post__author__profile', 'comment__author__profile',
    ).filter(user=request.user).order_by("-id")
    LentaLastView.update_last_view(request.user)
    return {
        'object_list': notifs
    }

@render_to('search.html')
@paginate(style='digg', per_page=10)
def search(request):
    """New sexy search"""
    form = SearchForm(request.GET)
    try:
        search_qs = SearchQuerySet().models(Post)
    except InvalidIndexError:
        search_qs = None
    if not form.is_valid() or not search_qs:
        return {
            'form': form,
            'query': '',
            'object_list': Post.objects.all(),
        }
    q = lambda attr: models.Q(**{attr: form.cleaned_data['query']})#SHIT
    return {
        'object_list': search_qs.filter_or(q('text') | q('preview') | q('raw_tags') | q('title')),
        'form': form,
        'query': form.cleaned_data['query'],
    }

    