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
from django.shortcuts import get_object_or_404
from jsonrpc import jsonrpc_method
from main.models import Post, Comment, Blog
from main.utils import Access


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
            action(obj, request.user, value)
            return {
                'id': id,
                'value': obj.get_rate(),
            }
        else:
            return {
                'error': True,
            }
    return rate_fnc

rate_post = rate_view_factory('rate_post', Post, Access.rate_post, Post.rate_post)
rate_comment = rate_view_factory('rate_comment', Comment, Access.rate_comment, Comment.rate_comment)
rate_blog = rate_view_factory('rate_blog', Blog, Access.rate_blog, Blog.rate_blog)
