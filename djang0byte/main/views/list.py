# -*- coding: utf-8 -*-
from django.db import transaction
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from main.models import *

def users(request, frm = 0, order = None, param = None, param_value = None):
    """Users list with params"""
    if order == 'rate':
        order_query = '(rate+blogs_rate*%d+posts_rate*%d+comments_rate*%d)' % (0.5, 0.3, 0.1)
    elif order == 'rate_desc':
        order_query = '-(rate+blogs_rate*%d+posts_rate*%d+comments_rate*%d)' % (0.5, 0.3, 0.1)
    elif order == 'name_desc':
        order_query = '-user_name'
    else:
        order_query = 'user_name'
    if param == 'city':
        pass
       # users = Profile.objects.filter(city.name=param_value).order_by(order_query)[frm:][:100]
    else:
        users = Profile.objects.order_by(order_query)[frm:][:100]
    return render_to_response('list.html', {'items': users, 'type': 'users', 'param': param, 'param_value': param_value, 'order': order})

def blogs(request, frm = 0, order = None, param = None, param_value = None):
    """Blogs list with params"""
    if order == 'rate':
        order_query = 'rate'
    elif order == 'rate_desc':
        order_query = '-rate'
    elif order == 'name_desc':
        order_query = '-name'
    else:
        order_query = 'name'
    blogs = Blog.objects.order_by(order_query)[frm:][:100]
    return render_to_response('list.html', {'items': blogs, 'type': 'blogs', 'param': param, 'param_value': param_value, 'order': order})
    
def cities(request, frm, order = None):
    """City list"""
    if order == 'name_desc':
        order_query = '-name'
    else:
        order_query = 'name'
    cities = City.objects.order_by(order_query)[frm:][:100]
    return render_to_response('list.html', {'items': cities, 'type': 'cities', 'param': None, 'param_value': None, 'order': order})
    
