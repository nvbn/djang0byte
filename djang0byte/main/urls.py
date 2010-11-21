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



from django.conf.urls.defaults import *
from djang0byte.main.views import *
#from django.contrib import admin
#admin.autodiscover()

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
  ('register/$', register),
  ('register/(.*)/$', register),
  ('user/(\w*)/$', profile),
  ('user/$', myprofile),
  ('login/$', login),
  ('logout/$', logout),
  ('login/(.*)/$', login),
  ('newblog/$', newblog),
  ('newpost/$', newpost),
  ('newpost/(.*)/$', newpost),
  ('newcomment/$', new_comment),
  ('newcomment/(\d*)/$', new_comment),
  ('newcomment/(\d*)/(\d*)/$', new_comment),
  ('friend/(\w*)/$', friend),
  ('edit/$', edit_user),
  ('action/(\w*)/(\d*)/(\w*)/$', action),
  ('action/(\w*)/(\d*)/$', action),
  ('install/', install),
  ('join/(\d*)/$', join),
  ('post/(\d*)/$', post),
  ('list/blogs/$', list_blogs),
  ('list/users/$', list_users),
  ('list/city/$', list_city),
  ('lenta/', lenta),
  ('myblogs/', myblogs),
  ('page/(.*)/$', text_page),
  ('(\w*)/([^\/]*)/$', post_list_with_param),
  ('(\w*)/$', post_list_with_param),
  ('$', post_list),
)
