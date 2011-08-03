# -*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_page
from annoying.decorators import render_to
from main.models import *
@cache_page(300)
@render_to('page.html')
def text_page(request, url):
    """Display text page with specified name

    Keyword arguments:
    request -- request object
    url -- String

    Returns: Array

    """
    text_page = TextPage.objects.get(url=url)
    return {
        'page': text_page
    }

@render_to('search.html')
def search(request):
    return {}