from django.test import TestCase
from django.db import models
from django.contrib.auth.models import User, Permission


class OrangePermissions(object):
    def can_change(self, obj, user):
        return obj.owner == user


class Orange(models.Model):
    owner = models.ForeignKey(User)

    perms = OrangePermissions()


class PermissionsCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='1')
        self.user_2 = User.objects.create(username='2')
        self.orange = Orange.objects.create(owner=self.user)
        self.user.user_permissions.add(
            Permission.objects.get_by_natural_key(
                'add_orange', 'object_permissions', 'orange',
            )
        )

    def test_defined_permission(self):
        self.assertTrue(self.user.can_change(self.orange))
        self.assertFalse(self.user_2.can_change(self.orange))

    def test_model_permission_on_object(self):
        self.assertTrue(self.user.can_add(self.orange))
        self.assertFalse(self.user_2.can_add(self.orange))

    def test_model_permission(self):
        self.assertTrue(self.user.can_add(Orange))
        self.assertFalse(self.user_2.can_add(Orange))

