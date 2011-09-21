from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset, login
from registration.views import register
from views import *
from forms import RegistrationFormProfile
import inspect
from functools import partial

if 'backend' in inspect.getargs(register.func_code).args:
    # hack for new django-registartion, still doesn't work for 0.8.0alpha
    register = partial(register, backend="django.contrib.auth.backends.ModelBackend")

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
    (r'^check/(.*)/(.*)/$', check)
)