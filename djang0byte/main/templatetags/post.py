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
from django import template
from main.models import LastView


register = template.Library()

@register.inclusion_tag('comments_count.html', takes_context=True)
def comments_count(context):
    """Spike for answers printing"""
    post = context['post']
    user = context['request'].user
    try:
        count = post.get_comment().count()
        if user.is_authenticated():
            try:
                new_count = post.get_comment().filter(
                    created__gt=LastView.objects.get(post=post, user=user).date
                ).count()
            except LastView.DoesNotExist:
                new_count = count
        else:
            new_count = -1
    except AttributeError:
        count = 0
        new_count = 0
    return {
        'count': count,
        'new_count': new_count
    }
