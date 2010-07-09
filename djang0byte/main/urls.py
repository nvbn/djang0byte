# -*- coding: utf-8 -*-
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
  ('login/(.*)/$', login),
  ('newblog/$', newblog),
  ('newpost/$', newpost),
  ('newpost/(.*)/$', newpost),
  ('newcomment/$', new_comment),
  ('newcomment/(\d*)/$', new_comment),
  ('newcomment/(\d*)/(\d*)/$', new_comment),
  ('post/(\d*)/$', post),
  ('(\w*)/([^\/]*)/$', post_list_with_param),
  ('$', post_list),
  ('install/', install),
  ('vote/$', vote)
)
