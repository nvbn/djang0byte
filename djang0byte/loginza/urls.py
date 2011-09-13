from django.conf.urls.defaults import *

from loginza import views

urlpatterns = patterns(
    '',
    url(r'return_callback/$', views.return_callback, name='loginza_return')
)
  