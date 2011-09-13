# -*- coding:utf-8 -*-
from django import http
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.utils.decorators import available_attrs
from django.utils.functional import wraps
from django.utils.http import urlquote
from django.contrib.sites.models import Site

from loginza import signals

def user_passes_test(test_func, login_url=None, fail_callback=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user passes the given test,
    redirecting to the log-in page if necessary. The test should be a callable
    that takes the user object and returns True if the user passes.
    """
    if not login_url:
        from django.conf import settings

        login_url = settings.LOGIN_URL

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if test_func(request.user):
                return view_func(request, *args, **kwargs)
            if fail_callback is not None:
                return fail_callback(request)
            else:
                path = urlquote(request.get_full_path())
                tup = login_url, redirect_field_name, path
                return http.HttpResponseRedirect('%s?%s=%s' % tup)

        return wraps(view_func, assigned=available_attrs(view_func))(_wrapped_view)

    return decorator


def _user_anonymous_callback(request):
    response = None

    results = signals.login_required.send(request)
    for callback, result in results:
        if isinstance(result, http.HttpResponse):
            response = result
            break

    if response is None:
        referer = request.META.get('HTTP_REFERER', '/')
        domain = Site.objects.get_current().domain
        abs_url = 'http://%s' % domain

        back_url = referer.replace(abs_url, '')
        response = http.HttpResponseRedirect(back_url if request.path != back_url else '/')

    return response


def login_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """
    Decorator for views that checks that the user is logged in, redirecting
    to the log-in page if necessary.
    """
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated(),
        redirect_field_name=redirect_field_name,
        fail_callback=_user_anonymous_callback
    )
    if function:
        return actual_decorator(function)
    return actual_decorator
