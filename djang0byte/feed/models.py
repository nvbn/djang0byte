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

from django_push.publisher.feeds import Feed
from tagging.models import TaggedItem
from main.models import *
from settings import SITENAME
from django.utils.translation import ugettext as _

class PostFeed(Feed):
    title = SITENAME
    link = "/rss/"

    def get_object(self, request, type = None, value = None):
        if BlogType.check(type):
            blog_type = BlogType.objects.get(name=type)
            self.description = _('Posts in %s') % (blog_type.name)
            return Post.objects.filter(blog__in=blog_type.get_blogs())
        if type == 'auth':
            self.description = _('Posts by %s') % (value)
            return Post.objects.filter(
                author=User.objects.get(username=value)
            )
        elif type == 'blog':
            self.description = _('Posts in blog %s') % (value)
            return Post.objects.filter(
                blog=Blog.objects.get(id=value)
            )
        elif type == 'tag':
            self.description = _('Posts with tag %s') % (value)
            return TaggedItem.objects.get_by_model(Post, value)
        else:
            return Post.objects.all()

    def items(self, obj):
        return obj.order_by('-id')[:50]

    def item_link(self, item):
        return "/post/%d/" % item.id

    def get_absolute_url(self, item):
        return "/post/%s/" % item.id

    def item_description(self, item):
        return item.preview
        
