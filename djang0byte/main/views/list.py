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
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from main.models import *
from django.views.decorators.cache import cache_page
from simplepagination import paginate
from annoying.decorators import render_to
from settings import POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT

@cache_page(0)
@render_to('list.html')
@paginate(style='digg', per_page=100)
def list_users(request, order = None, param = None, param_value = None):
    """Users list with params

    Keyword arguments:
    request -- request object
    order -- String
    param -- String
    param_value -- String

    Returns: Array

    """
    if order not in ('rate', 'rate_desc', 'name', 'mane_desc'):
        param_value = param
        param = order
        
    if param == 'city':
        items = Profile.objects.select_related('user').filter(city=City.objects.get(name=param_value))
        url = '/list/users/city/%s/' % (param_value, )
    else:
        items = Profile.objects.select_related('user')
        url = '/list/users/'
    if order == 'rate':
        items = items.extra(select={'fullrate':
                'rate+%f*posts_rate+%f*blogs_rate+%f*comments_rate'
                % (POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT), },
                order_by=['-fullrate',])
    elif order == 'rate_desc':
        items = items.extra(select={'fullrate':
               'rate+%f*posts_rate+%f*blogs_rate+%f*comments_rate'
                % (POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT), },
                order_by=['fullrate',])
    elif order == 'name_desc':
        items = items.order_by('-user__username')
    else:
        items = items.order_by('user__username')

    return({'object_list': items, 'type': 'users', 'param': param,
            'param_value': param_value, 'order': order, 'url': url})


@cache_page(0)
@render_to('list.html')
@paginate(style='digg', per_page=100)
def list_blogs(request, order = None, param = None, param_value = None):
    """Blogs list with params

    Keyword arguments:
    request -- request object
    order -- String
    param -- Strign
    param_value -- String

    Returns: Array

    """
    if order == 'rate':
        order_query = 'rate'
    elif order == 'rate_desc':
        order_query = '-rate'
    elif order == 'name_desc':
        order_query = '-name'
    else:
        order_query = 'name'
    blogs = Blog.objects.order_by(order_query)
    if param == 'my':
        blogs = blogs.filter(owner=request.user)
        url = '/myblogs/'
    else:
        url = '/list/blogs/'
    return({'object_list': blogs, 'type': 'blogs', 'param': param,
            'param_value': param_value, 'order': order, 'url': url})

@cache_page(0)
@render_to('list.html')
@paginate(style='digg', per_page=100)
def list_city(request, order = None):
    """City list

    Keyword arguments:
    request -- request object
    order -- String

    Returns: Array

    """
    if order == 'rate_desc':
        order_query = '-count'
    elif order == 'rate':
        order_query = 'count'
    elif order == 'name_desc':
        order_query = '-name'
    else:
        order_query = 'name'
    print order_query
    cities = City.objects.order_by(order_query)
    return({'object_list': cities, 'type': 'cities', 'param': None,
            'param_value': None, 'order': order, 'url': '/list/city/'})

@login_required
def myblogs(request, order = None):
    """Return users blogs, wrap on list_blogs

    Keyword arguments:
    request -- request object
    order -- String

    Returns: Array

    """
    return(list_blogs(request, order, 'my'))