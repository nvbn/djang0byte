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
from django.conf import settings
from django.contrib import admin
from feed.models import PostFeed
from django.conf.urls.defaults import *
from jsonrpc import jsonrpc_site


import main.rpc_views

admin.autodiscover()

urlpatterns = patterns('',
    (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': 'media/'}),
    (r'^admin/', include(admin.site.urls)),
    (r'^accounts/', include('register.urls')),
    (r'^tagging_autocomplete/', include('tagging_autocomplete.urls')),
    (r'^rss/(.*)/(.*)/$', PostFeed()),
    (r'^rss/(.*)/$', PostFeed()),
    (r'^rss/$', PostFeed()),
    (r'^pm/', include('messages.urls')),
    (r'^loginza/', include('loginza.urls')),
    (r'^', include('main.urls')),
)


if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/nvbn/work/djang0byte/djang0byte/media/'}),
    )


