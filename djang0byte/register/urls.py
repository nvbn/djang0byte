from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset, login
from registration.views import register
from views import *
from forms import RegistrationFormProfile

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