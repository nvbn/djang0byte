from django.db import models
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.utils.translation import ugettext as _
from itertools import ifilter
from shortcuts import get_module_name
from functools import wraps
import types


def render_to(template, mimetype=None):
    """
    Decorator for Django views that sends returned dict to render_to_response function
    with given template and RequestContext as context instance.

    If view doesn't return dict then decorator simply returns output.
    Additionally view can return two-tuple, which must contain dict as first
    element and string with template name as second. This string will
    override template name, given as parameter

    Parameters:

     - template: template name to use
    """
    
    def template_name(func):
        return "%s/%s.html" % (get_module_name(func), func.__name__)
    
    def render(request, output, template):        
        if isinstance(output, (list, tuple)):
            return render_to_response(output[1], output[0], RequestContext(request))
        elif isinstance(output, dict):
            tmpl = output.pop('TEMPLATE', template)
            return render_to_response(tmpl, output, RequestContext(request), mimetype=mimetype)
        return output        
        
    if isinstance(template, types.FunctionType):
        func = template
        @wraps(func)
        def wrapper(request, *args, **kw):
            return render(request, func(request, *args, **kw), template_name(func))
        return wrapper

    def renderer(func):
        def wrapper(request, *args, **kw):
            return render(request, func(request, *args, **kw), template)
        wrapper.__module__ = func.__module__
        wrapper.__name__ = func.__name__
        return wrapper
    return renderer


def extend(model, no_meta=False):
    """Extend exist model"""
    def decorator(cls):
        for (attr, val) in ifilter(lambda (attr, val): attr[0:2] != '__', cls.__dict__.items()):
            if issubclass(type(val), models.Field):
                model.add_to_class(attr, val)
            elif attr == 'Meta' and not no_meta:
                extend(model._meta)(val)
            else:
                setattr(model, attr, val)
        return None
    return decorator
