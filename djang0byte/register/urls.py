from django.conf.urls.defaults import *
from django.contrib.auth.views import password_reset
from registration.views import register
from views import *
from forms import RegistrationFormProfile

urlpatterns = patterns('',
    url(r'^register/$', register,
        {'form_class': RegistrationFormProfile},
        name='registration.views.register'),
    (r'^logout/', logout),
    (r'', include('registration.urls')),
    (r'^check/(.*)/(.*)/(.*)/$', check),
    (r'^check/(.*)/(.*)/$', check)
)