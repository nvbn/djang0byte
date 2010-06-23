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
  ('user/(.*)/$', profile),
  ('user/$', myprofile),
  ('login/$', login),
  ('login/(.*)/$', login),
  ('newblog/$', newblog),
  ('newpost/$', newpost),
)
