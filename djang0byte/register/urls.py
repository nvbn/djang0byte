from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset, login
from registration.views import register as int_register
from views import *
from forms import RegistrationFormProfile
import inspect
from functools import partial
from django.http import HttpResponseRedirect
from django.conf import settings

if 'backend' in inspect.getargs(int_register.func_code).args:
    # hack for new django-registartion, still doesn't work for 0.8.0alpha
    int_register = partial(int_register, backend="django.contrib.auth.backends.ModelBackend")

def register(request, *args, **kwargs):
    if request.user.is_authenticated():
        return HttpResponseRedirect("/")
    return int_register(request, *args, **kwargs)

urlpatterns = patterns('',
    url(r'^register/$', register,
        {'form_class': RegistrationFormProfile},
        name='registration.views.register'),
    (r'^logout/', logout),
    url(r'^login/js/$',
        login,
        {'template_name': 'registration/login_form.html'},
    name='auth_login'),
    (r'', include('registration.urls')),
    (r'^check/(.*)/(.*)/(.*)/$', check),
    (r'^check/(.*)/(.*)/$', check),
)

if getattr(settings, 'ALLOW_MERGING', False):
    urlpatterns += patterns('',
        url(r'^merge_key/$', 'register.views.generate_merge_key', name='register_merge_key'),
        url(r'^merge/$', 'register.views.merge', name='merge'),
    )
