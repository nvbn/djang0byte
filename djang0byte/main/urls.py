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
from django.conf.urls.defaults import patterns, url

urlpatterns = patterns('djang0byte.main.views',
  ('^user/(.*)/$', 'profile'),
  ('^newblog/$', 'newblog'),
  ('^newpost/$', 'newpost'),
  ('^newpost/(.*)/$', 'newpost'),
  ('^newcomment/$', 'new_comment'),
  ('^newcomment/(\d*)/$', 'new_comment'),
  ('^newcomment/(\d*)/(\d*)/$', 'new_comment'),
  ('^action/join/(\d*)/$', 'join'),
  ('^action/friend/(.*)/$', 'friend'),
  ('^action/edit_user/$', 'edit_user'),
  ('^action/edit_post/(\d*)/$', 'edit_post'),
  ('^action/edit_comment/(\d*)/$', 'edit_comment'),
  ('^action/change_userpic/$', 'change_userpic'),
  ('^action/delete_userpic/$', 'delete_userpic'),
  ('^action/change_password/$', 'password_change'),
  ('^action/get_val/(.*)/(.*)/$', 'get_val'),
  ('^action/get_val/(.*)/$', 'get_val'),
  ('^action/get_users/(.*)/$', 'get_users'),
  ('^action/delete_post/(\d*)/$', 'delete_post'),
  ('^action/delete_draft/(\d*)/$', 'delete_draft'),
  ('^action/delete_comment/(\d*)/$', 'delete_comment'),
  ('^action/preview_comment/$', 'preview_comment'),
  ('^action/post_options/(\d*)/$', 'post_options'),
  ('^action/get_last_comments/(\d*)/$', 'get_last_comments'),
  ('^action/mark_solved/(\d*)/(\d*)/$', 'mark_solved'),
  ('^action/set_right_answer/(\d*)/(\d*)/(\d*)/$', 'set_right_answer'),
  ('^action/get_raters/(\w*)/(\d*)/$', 'get_raters'),
  ('^action/(\w*)/(\d*)/(.*)/$', 'action'),
  ('^action/(\w*)/(\d*)/$', 'action'),
  url(r'^post/(?P<id>\d*)/$', 'post', name='main_post'),
  ('^comments/(.*)/$', 'comments'),
  ('^list/blogs/$', 'list_blogs'),
  ('^list/blogs/(.*)/$', 'list_blogs'),
  ('^list/users/(.*)/(.*)/(.*)/$', 'list_users'),
  ('^list/users/(.*)/(.*)/$', 'list_users'),
  ('^list/users/(.*)/$', 'list_users'),
  ('^list/users/$', 'list_users'),
  ('^list/city/(.*)/(.*)/$', 'list_city'),
  ('^list/city/(.*)/$', 'list_city'),
  ('^list/city/$', 'list_city'),
  ('^lenta/', 'lenta'),
  ('^myblogs/$', 'myblogs'),
  ('^myblogs/(.*)/$', 'myblogs'),
  ('^draft/(\d*)/$', 'edit_draft'),
  ('^draft/', 'draft'),
  ('^page/(.*)/$', 'text_page'),
  ('^search/$', 'search'),
  ('^(\w*)/([^\/]*)/$', 'post_list_with_param'),
  ('^(\w*)/$', 'post_list_with_param'),
  ('^$', 'post_list'),
)
