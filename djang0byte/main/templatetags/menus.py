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




from django.template import Library
from datetime import datetime, timedelta
from timezones.utils import localtime_for_timezone
from main.models import Post
from functools import partial
#TODO:rewrite this hardcoded shit
register = Library()


@register.filter
def menu_class(url, current_url):
    """
        kostil =)
    """
    urls = [
        '/',
        '/answer/',
        '/talks/',
        '/lenta/',
    ]
    if url == current_url:
        return 'current'
    try:
        id = urls.index(current_url) - 1
        if id >= 0 and urls[id] == url:
            return 'previos'
        else:
            return ''
    except ValueError:
        return url == '/' and 'current' or ''


@register.filter
def menu_count(url):
    """
        kostil =)
    """
    date = datetime.now() - timedelta(days=1)
    qs_fnc = partial(Post.objects.filter, date__gte=date)
    count_funcs = {
        '/': qs_fnc(blog__type__display_default=True).count,
        '/answer/': qs_fnc(blog__type__name='answer').count,
        '/talks/': qs_fnc(blog__type__name='talks').count,
        '/lenta/': lambda: -5,
    }
    print count_funcs.get(url)()
    return  count_funcs.get(url)()