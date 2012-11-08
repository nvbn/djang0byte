def extend(model):
    """Extend exist model"""
    def decorator(cls):
        for (attr, val) in ifilter(lambda (attr, val): attr[0:2] != '__', cls.__dict__.items()):
            if issubclass(type(val), models.Field):
                model.add_to_class(attr, val)
            elif attr == 'Meta':
                extend(model._meta)(val)
            else:
                setattr(model, attr, val)
        return None
    return decorator
