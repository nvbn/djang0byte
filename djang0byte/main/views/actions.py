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
from django.shortcuts import render_to_response, get_object_or_404
from django.template.loader import render_to_string
from main.forms import *
from main.models import *
from djang0parser.utils import unparse, unparse, remove_code
from settings import POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT, VALID_TAGS, VALID_ATTRS
from django.views.decorators.cache import cache_page, never_cache
from simplepagination import paginate
from annoying.decorators import render_to
from tagging.models import TaggedItem
from main.utils import Access, jsend, RATE
from djang0parser import utils
from django.template import RequestContext
from settings import DEFAULT_CACHE_TIME
from django.views.decorators.vary import vary_on_cookie
from django.utils import simplejson
from django.utils.translation import gettext as _
from annoying.decorators import ajax_request
import simplejson as json
from django.conf import settings
from django.core.urlresolvers import reverse


@never_cache
def rate_comment(request, profile, comment_id, json, action):
    """Rate post

    Keyword arguments:
    request -- request object
    profile -- Profile
    comment_id -- Integer
    json -- Boolean

    Returns: HttpResponse

    """
    comment = Comment.objects.select_related('post').get(id=comment_id)
    if request.user != comment.author:
        if profile.check_access(Access.rate_comment):
            rate = comment.rate_comment(request.user, RATE[action])
            error = ''
            if not rate:
                error = _('Second vote is forbidden!')
            if json:
                return jsend({'error': error, 'rate': comment.rate, 'id': comment.id })
            else:
                return HttpResponseRedirect('%s#cmnt%d' % (
                    reverse('main_post', args=(comment.post.id,)),
                int(id)))
        else:
            return jsend({
                'error': _('Not allow this action!')
            })
    elif json:
        return jsend({
            'error': _('For their comments can not vote!')
        })
    return HttpResponseRedirect('%s#cmnt%d' % (
        reverse('main_post', args=(comment.post.id,)),
    comment.id))

@never_cache
def rate_post(request, profile, post, json, action):
    """Rate post

    Keyword arguments:
    request -- request object
    profile -- Profile
    post -- Post
    json -- Boolean

    Returns: HttpResponse

    """
    if request.user != post.author:
        if profile.check_access(Access.rate_post):
            rate = post.rate_post(request.user, RATE[action()])
            error = ''
            if not rate:
                error = _('Second vote is forbidden!')
            if json:
                return jsend({
                    'error': error,
                    'rate': post.rate,
                    'id': post.id
                })
        elif json:
            return jsend({
                'error': _('Not allow this action!')
            })
    elif json:
        return jsend({
            'error': _('For their post can not vote!')
        })
    return HttpResponseRedirect(
        reverse('main_post', args=(post.id,))
    )

@never_cache
def rate_blog(request, profile, blog_id, json, action):
    """Rate post

    Keyword arguments:
    request -- request object
    profile -- Profile
    blog_id -- Integer
    json -- Boolean

    Returns: HttpResponse

    """
    blog = Blog.objects.get(id=blog_id)
    if request.user != blog.owner:
        if profile.check_access(Access.rate_blog):
            rate = blog.rate_blog(request.user, RATE[action])
            error = ''
            if not rate:
                error = _('Second vote is forbidden!')
            if json:
                return jsend({
                    'error': error,
                    'rate': blog.rate,
                    'id': blog.id
                })
        elif json:
            return jsend({
                'error': _('Not allow this action!')
            })
    elif json:
        return jsend({
            'error': _('For their blog can not vote!')
        })
    return HttpResponseRedirect('/blog/%d/' % (int(blog_id)))

@login_required
def preview_comment(request):
    return jsend({'text':utils.parse(request.POST.get('text'), VALID_TAGS, VALID_ATTRS)})

@never_cache
def action(request, type, id, action = None):#TODO: Split and rewrite this shit!
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
    if not request.user.is_authenticated():
        if json:
            return jsend({
                'error': _('Please register for this action!')
            })
        else:
            return HttpResponseRedirect('/')
    try:
        post = Post.objects.select_related('author').get(id=id)
    except Post.DoesNotExist:
        post = Post()
    profile = Profile.objects.get(user=request.user)
    if type == 'ratecom':
        return(rate_comment(request, profile, id, json, action))
    elif type == 'rateblog' and profile.check_access(Access.rate_blog):
        return(rate_blog(request, profile, id, json, action))
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
        try:
            spy = Spy.objects.get(post=post, user=request.user)
            spy.delete()
        except Spy.DoesNotExist:
            spy = Spy()
            spy.post = post
            spy.user = request.user
            spy.save()
    elif type == 'ratepost':
        return rate_post(request, profile, post, json, action)
    elif type == 'answer':
        answers = Answer.objects.filter(post=post)
        if post.type == Post.TYPE_ANSWER:
            answers.get(id=request.POST.get('answ')).vote(request.user)
        elif post.type == Post.TYPE_MULTIPLE_ANSWER:
            for answer in answers:
                if request.POST.get('answ_' + str(answer.id), 0):
                    answer.vote(request.user, True)
                answer.fix(request.user)
    elif type == 'refrain':
        vote = AnswerVote()
        vote.answer = post
        vote.user = request.user
        vote.save()

    return HttpResponseRedirect('/post/%d/' % (int(id)))

@never_cache
@login_required
def edit_post(request, id):
    """Edit post

    Keyword arguments:
    request -- request
    id -- int -- post.id

    Returns: HttpResponse
    """
    try:
        if request.user.has_perm('main.change_post'):
            post = Post.objects.get(id=id, type__lt='3')
        else:
            post = Post.objects.get(id=id, author=request.user, type__lt='3')
    except Post.DoesNotExist:
        return HttpResponseRedirect('/post/%d/' % (int(id)))
    form = post_forms[post.type]
    if request.method == 'POST':
        form = form(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            remove_code(post.text)
            remove_code(post.preview)
            post.set_data(data)
            if request.user.has_perm('main.edit_post'):
                post.set_blog(data['blog'], force=True)
            post.save(edit=True, retry=True)
            post.set_tags(data['tags'])
            return HttpResponseRedirect('/post/%d/' % (post.id))
        else:
            return render_to_response('newpost.html', {
                'form': form,
                'blogs': Blog.create_list(request.user.get_profile(), post.blog == None or post.blog.id, append=post.blog),
                'type': post.type,
                'extend': 'base.html',
                'edit': True
            }, context_instance=RequestContext(request))
    else:
        if post.text.find('<fcut>') >= 0:
            post.text = post.preview + post.text
        #TODO: stay fcut and cut tag in editor
        data = {
            'tags': ', '.join(map(lambda x: x.__unicode__(), post.get_tags())),
            'title': post.title,
            'text': unparse(post.text),
            'addition': post.addition
        }
        form = form(data)
        return render_to_response('newpost.html', {
            'form': form,
            'blogs': Blog.create_list(request.user.get_profile(), post.blog == None or post.blog.id, append=post.blog),
            'type': post.type,
            'extend': 'base.html',
            'edit': True,
            'id': post.id
        }, context_instance=RequestContext(request))

@never_cache
def get_val(request, type, count=20):
    out = []
    print type
    try:
        del request.session['right_panel']
    except KeyError:
        pass
    if type == 'comments':
        request.session['right_panel'] = type
        comments = Comment.objects.exclude(depth=1).select_related('post', 'post.blog', 'post.author').order_by('-id')[
                   :count]
        for comment in comments:
            out.append({
                'title': u"%s / %s &ndash; %s" % (
                    comment.author.username,
                    comment.post.blog and comment.post.blog.name or comment.post.author.username,
                    comment.post.title,
                ),
                'url': "/post/%d/#cmnt%d" % (
                    comment.post.id,
                    comment.id,
                ),
                'rate': comment.rate,
                'type': 'comment',
            })
    elif type == 'posts':
        request.session['right_panel'] = type
        posts = Post.objects.select_related('blog', 'author').order_by('-id')[:count]
        for post in posts:
            out.append({
                'title': u"%s &ndash; %s" % (
                    post.blog and post.blog.name or post.author.username,
                    post.title,
                ),
                'url': '/post/%d/' % (post.id,),
                'rate': post.rate,
                'type': 'post',
            })
    elif type == 'users':
        request.session['right_panel_2'] = 'users'
        users = Profile.objects.select_related('user').extra(select={'fullrate':
            "rate+%f*posts_rate+%f*blogs_rate+%f*comments_rate"
            % (POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT), },
            order_by=['-fullrate',])[:count]
        for user in users:
            out.append({
                'title': user.user.username,
                'url': '/user/%s/' % (user.user.username,),
                'rate': user.get_rate(),
                'type': 'user',
            })
    elif type == 'blogs':
        request.session['right_panel_2'] = 'blogs'
        blogs = Blog.objects.order_by('-rate')[:count]
        for blog in blogs:
            out.append({
                'title': blog.name,
                'url': "/blog/%d/" % (blog.id,),
                'rate': blog.rate,
                'type': 'blog',
            })
    elif type == 'favourites':
        favourites = Favourite.objects.select_related('post').filter(user=request.user).order_by('-id')[:count]
        request.session['right_panel'] = type
        for favourite in favourites:
           out.append({
                'title': favourite.post.title,
                'url': "/post/%d/" % (favourite.post.id,),
                'rate': favourite.post.rate,
                'type': 'favourite',
            })
        out.append({
                'title': _("Show all!"),
                'url': "/favourite/",
                'rate': 0,
                'type': 'title',
            })
    elif type == 'spies':
        favourites = Spy.objects.select_related('post').filter(user=request.user).order_by('-id')[:count]
        request.session['right_panel'] = type
        for favourite in favourites:
           out.append({
                'title': favourite.post.title,
                'url': "/post/%d/" % (favourite.post.id,),
                'rate': favourite.post.rate,
                'type': 'spy',
            })
    elif type == 'drafts':
        drafts = Draft.objects.filter(author=request.user, is_draft=True).order_by('-id')[:count]
        request.session['right_panel'] = type
        for draft in drafts:
           out.append({
                'title': draft.title,
                'url': "/draft/%d/" % (draft.id,),
                'rate': 0,
                'type': 'draft',
            })
        out.append({
                'title': _("Show all!"),
                'url': "/draft/",
                'rate': 0,
                'type': 'title',
            })
    return jsend(out)


@login_required
def get_last_comments(request, post, comment_id = None):
    post = Post.objects.get(id=post)
    try:
        last_view = LastView.objects.get(post=post, user=request.user)
        last_view_date = last_view.date
        last_view.update()
    except:
        last_view = LastView(post=post, user=request.user)
        last_view_date = 1
        last_view.save()
    comments = Comment.objects.filter(created__gt=last_view_date, post=post).order_by('created')
    return jsend({
        'comments': [{
            'content': render_to_string('single_comment.html', {
                'post': post,
                'comment': comment,
                'last_view': last_view_date,
            }, RequestContext(request)),
            'placeholder': comment.get_placceholder().id,
            'id': comment.id,
            'own': comment_id == comment.id,
        } for comment in comments],
        'count': comments.count(),
    })


@never_cache
def get_users(request, users):
    out = []
    for username in users.split(','):
        try:
            user = User.objects.get(username=username)
            profile = user.get_profile()
            out.append({
                'name': username,
                'is_active': user.is_active,
                'avatar': profile.get_avatar(),
                'rate': profile.get_rate(),
            })
        except User.DoesNotExist:
            pass
    return jsend(out)

@never_cache
@render_to('post_options.html')
@login_required
def post_options(request, id):
    extend = 'base.html'
    if request.GET.get('json', 0):
        extend = 'json.html'
    if not request.user.has_perm('main.delete_post'):
        return {}
    post = Post.objects.get(id=id)
    if request.method == 'POST':
        form = PostOptions(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            post.disable_rate = data['disable_rate']
            post.disable_reply = data['disable_reply']
            post.pinch = data['pinch']
            post.save()
            return HttpResponseRedirect('/post/%d/' % (post.id))
    else:
        data = {
            'disable_rate': post.disable_rate,
            'disable_reply': post.disable_reply,
            'pinch': post.pinch
        }
        form = PostOptions(data)
    return {
        'form': form,
        'extend': extend,
        'id': post.id
    }

@never_cache
@render_to('delete_post.html')
@login_required
def delete_post(request, id):
    extend = 'base.html'
    if request.GET.get('json', 0):
        extend = 'json.html'
    if request.user.has_perm('main.delete_post'):
        post = Post.objects.get(id=id)
        if request.POST.get('yes'):
            post.delete()
            return HttpResponseRedirect('/')
        elif not request.POST.get('no'):
            return {
                'extend': extend,
                'post': post
            }
    return HttpResponseRedirect('/post/%d/' % (int(id)))

@never_cache
@render_to('delete_comment.html')
@login_required
def delete_comment(request, id):
    extend = 'base.html'
    if request.GET.get('json', 0):
        extend = 'json.html'
    if request.user.has_perm('main.delete_comment'):
        comment = Comment.objects.select_related('post').get(id=id)
        if request.POST.get('yes'):
            post = comment.post
            comment.delete()
            return HttpResponseRedirect('/post/%d/' % (post.id,))
        elif not request.POST.get('no'):
            return {
                'extend': extend,
                'comment': comment
            }
    return HttpResponseRedirect('/post/%d/#cmnt%d' % (comment.post.id, int(id)))

@never_cache
@render_to('new_comment.html')
@login_required
def edit_comment(request, id):
    """Edit comment view

    Keyword arguments:
    request - -request
    id -- int -- comment.id

    Returns: HttpResponse
    """
    if request.user.has_perm('main.change_comment'):
        comment = Comment.objects.select_related('post').get(id=id)
        if request.method == 'POST':
            form = CreateCommentForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                comment.text = utils.parse(data['text'], VALID_TAGS, VALID_ATTRS)
                comment.save()
                return HttpResponseRedirect('/post/%d/' % (comment.post.id))
        else:
            text = utils.unparse(comment.text)
            data = {
                'post': comment.post.id,
                'text': text
            }
            form = CreateCommentForm(data)
    return {
        'edit': True,
        'form': form,
        'cid': id,
        'extend': 'base.html'
    }

@login_required
def mark_solved(request, post_id, mark=1):
    """Mark or unmark Q&A post solved

    Keywords Arguments:
    post_id -- int
    mark -- bool

    Returns: redirect
    """
    mark = int(mark)
    post = get_object_or_404(
        Post,
        id=post_id,
        author=request.user,
        blog__type__is_qa=True,
    )
    post.solved = mark
    post.save(convert=True)
    return HttpResponseRedirect('/post/%d' % (post.id,))

@login_required
def set_right_answer(request, post_id, comment_id, reason=0):
    """Set right answer comment

    Keywords Arguments:
    post_id -- int
    comment_id -- int
    reason -- bool

    Returns: redirect
    """
    reason = int(reason)
    post = get_object_or_404(
        Post,
        id=post_id,
        author=request.user,
    )
    comment = get_object_or_404(
        Comment,
        id=comment_id,
        post=post,
    )
    if reason:
        post.right_answer = comment
    else:
        post.right_answer = None
    post.save(convert=True)
    return HttpResponseRedirect('/post/%d' % (post.id,))

@ajax_request
def get_raters(request, obj_type, obj_id):
    """Get json of raters

    Keywords Arguments:
    obj_type -- str in post, comment, blog, user
    obj_id -- int

    Returns: json
    """
    if getattr(settings, 'PRIVATE_RATING', True):
        return HttpResponseRedirect('/')
    if obj_type == 'post':
        type_model = Post
    elif obj_type == 'comment':
        type_model = Comment
    elif obj_type == 'blog':
        type_model = Blog
    elif obj_type == 'user':
        type_model = Profile
    else:
        return {
            'error': True,
        }
    obj = get_object_or_404(type_model, id=obj_id)

    return {#TODO: use json serializable class
        'raters': map(
            lambda rate: {
                'avatar': rate.user.get_profile().get_avatar(),
                'username': rate.user.username,
                'negative': rate.negative,
            },
            obj.get_rates().select_related('user__profile')
        )
    }