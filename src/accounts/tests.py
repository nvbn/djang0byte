from django.test import TestCase
from django.contrib.auth.models import User
from accounts.remote_services import get_service


class RemoteServiceTest(TestCase):
    def test_dummy(self):
        """Check dummy service"""
        service = get_service('http://nvbn.info/')
        self.assertEqual(service.description, None)

    def test_lastfm(self):
        """Check lastfm service"""
        service = get_service('http://www.lastfm.ru/user/nvbn')
        self.assertIsNotNone(service.description)
        self.assertGreater(len(service.description), 3)
