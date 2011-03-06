from django.conf.urls.defaults import *
from registration.views import register
from views import *
from captcha.forms import RegistrationFormCaptcha

urlpatterns = patterns('',
    url(r'^register/$', register,
        {'form_class': RegistrationFormCaptcha},
        name='registration.views.register'),
    (r'', include('registration.urls')),
    (r'^check/(.*)/(.*)/(.*)/$', check),
    (r'^check/(.*)/(.*)/$', check)
)