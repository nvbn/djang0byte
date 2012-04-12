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
from functools import wraps
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404
from jsonrpc import jsonrpc_method
from main.models import Post, Comment, Blog, Favourite, Spy, Profile, Draft
from main.utils import Access
from main.forms import PostOptions
from baseutils.jrpc import to_json
from django.utils.translation import ugettext as _
from django.conf import settings
from djang0parser import utils


def rate_view_factory(method, cls, permission, action):
    """Rate views factory"""
    @jsonrpc_method(
        'main.%s(id=int, value=bool) -> dict' % method,
        authenticated=True,
    )
    def rate_fnc(request, id, value):
        """Rate function"""
        value = +1 if value else -1
        obj = get_object_or_404(cls, id=id)
        if request.get_profile.check_access(permission):
            if action(obj, request.user, value):
                return to_json(obj)
            else:
                return {
                    'error': _(u'Rating allowed once a time')
                }
        else:
            return {
                'error': _(u'Permission denied'),
            }
    return rate_fnc

rate_post = rate_view_factory('rate_post', Post, Access.rate_post, Post.rate_post)
rate_comment = rate_view_factory('rate_comment', Comment, Access.rate_comment, Comment.rate_comment)
rate_blog = rate_view_factory('rate_blog', Blog, Access.rate_blog, Blog.rate_blog)


@jsonrpc_method(
    'main.preview_comment(text=unicode) -> dict',
    authenticated=True,
)
def preview_comment(request, text):
    """Get comment preview"""
    return {
        'text': utils.parse(
            text,
            settings.VALID_TAGS,
            settings.VALID_ATTRS,
        )
    }


def change_action_factory(method, model):
    """Change action rpc views factory"""
    @jsonrpc_method(
        'main.%s(post_id=int) -> dict' % method,
        authenticated=True,
    )
    def change_action(request, post_id):
        post = get_object_or_404(Post, id=post_id)
        try:
            obj = model.objects.get(
                user=request.user, post=post,
            )
            obj.delete()
        except model.DoesNotExist:
            model.objects.create(
                user=request.user, post=post,
            )
        return to_json(post)
    return change_action


change_favourite = change_action_factory('change_favourite', Favourite)
change_spy = change_action_factory('change_spy', Spy)


def get_val(method, panel_type, panel_key=''):
    """Get api value decorator"""
    def decorator(fnc):
        @wraps(fnc)
        @jsonrpc_method('main.%s(count=int, panel=bool) -> list' % method)
        def wrapper(request, count=20, panel=False):
            if not 0 < count < 100:
                count = 20
            if panel:
                request.session['right_panel%s' % panel_key] = panel_type
            return map(to_json, fnc(request, count))
        return wrapper
    return decorator


@get_val('get_last_comments', 'comments')
def get_last_comments(request, count):
    """Get last comments"""
    return Comment.objects.exclude(depth=1).select_related(
        'post', 'post.blog', 'post.author',
    ).order_by('-id')[:count]


@get_val('get_last_posts', 'posts')
def get_last_posts(request, count):
    """Get last posts"""
    return Post.objects.select_related(
        'blog', 'author',
    ).order_by('-id')[:count]


@get_val('get_users', 'users', '_2')
def get_users(request, count):
    """Get users"""
    return Profile.objects.select_related('user').extra(
        select={
            'fullrate': "rate+%f*posts_rate+%f*blogs_rate+%f*comments_rate" % (
                settings.POST_RATE_COEFFICIENT,
                settings.BLOG_RATE_COEFFICIENT,
                settings.COMMENT_RATE_COEFFICIENT),
            },
        order_by=['-fullrate'],
    )[:count]


@get_val('get_blogs', 'blogs', '_2')
def get_blogs(request, count):
    """Get blogs"""
    return Blog.objects.order_by('-rate')[:count]


@login_required
@get_val('get_favourites', 'favourites')
def get_favourites(request, count):
    """Get favourites"""
    return Post.objects.filter(
        favourite__user=request.user,
    ).order_by('-favourite__id')[:count]


@login_required
@get_val('get_spies', 'spies')
def get_spies(request, count):
    """Get spied posts"""
    return Post.objects.filter(
        spy__user=request.user,
    ).order_by('-spy__id')[:count]


@login_required
@get_val('get_drafts', 'drfats')
def get_drafts(request, count):
    """Get drafts"""
    return Draft.objects.filter(
        author=request.user, is_draft=True,
    ).order_by('-id')[:count]


@jsonrpc_method(
    'main.join_blog(blog_id=int) -> dict',
    authenticated=True,
)
def join_blog(request, blog_id):
    """Join or withdraw blog"""
    blog = get_object_or_404(Blog, id=blog_id)
    blog.add_or_remove_user(request.user)
    return {
        'status': True,
    }


@permission_required('post.can_change_options')
@jsonrpc_method(
    'main.post_options(post_id=int, disable_rate=bool, disable_reply=bool, pinch=bool) -> dict',
    authenticated=True,
)
def post_options(request, post_id, disable_rate, disable_reply, pinch):
    """Change post options"""
    post = get_object_or_404(Post, id=post_id)
    form = PostOptions({
        'disable_rate': disable_rate,
        'disable_reply': disable_reply,
        'pinch': pinch,
    }, instance=post)
    if form.is_valid():
        post = form.save()
        return to_json(post)
    else:
        return {
            'error': form.errors,
        }
