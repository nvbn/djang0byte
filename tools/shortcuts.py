def get_module_name(model):
    mod_name =  model.__module__.lower()
    mod =  mod_name.split(".")
    if mod[0]=="apps":
        mod = mod[1]
    elif mod_name.startswith("django.contrib"):
        mod = "%s_%s" % (mod[0],mod[2])
    else:
        mod = mod[0]
    return mod


def json_getattr(obj, attr):
    """Special getattr"""
    if  type(attr) in (list, tuple):
        name, attr = attr
    else:
        name = attr
    if hasattr(attr, '__call__'):
        val =  attr(obj)
    else:
        attr = getattr(obj, attr, None)
        if hasattr(attr, '__call__'):
            val = attr()
        else:
            val = attr
    return name, val


def to_json(obj, fields=None):
    """Serialize object to json"""
    if type(obj) in (list, dict, tuple, int, str, unicode, float) or obj == None:
        return obj
    if not (fields or hasattr(obj, 'json_fields')):
        raise TypeError('Set json_fields to your model!')
    if not fields:
        fields = obj.json_fields
    return dict(map(lambda attr:
        json_getattr(obj, attr),
    fields))
