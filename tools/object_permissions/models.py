from django.contrib.auth.models import User
from django.db import models
from tools.decorators import extend


@extend(User)
class PermissionProfile(object):
    """Extend user for object permissions support"""

    def _check_model_permission(self, name, model):
        """Check model permission"""
        return self.has_perm('%s.%s_%s' % (
            model._meta.app_label,
            name,
            model._meta.module_name,
        ))

    def _check_permission(self, name, obj):
        """Check permission"""
        try:
            if issubclass(obj, models.Model):
                return self._check_model_permission(name, obj)
        except TypeError:
            model_permission = self._check_model_permission(
                name, type(obj),
            )
            permission = getattr(obj, 'perms', None) 
            if permission:
                check = getattr(permission, 'can_%s' % name, None)
            else:
                check = None
            return model_permission or (check and check(obj, self))
        else:
            return False

    can_add = lambda self, obj: self._check_permission('add', obj)
    can_change = lambda self, obj: self._check_permission('change', obj)
    can_delete = lambda self, obj: self._check_permission('delete', obj)
