from django.test import TestCase
from django.contrib.auth.models import User
from tools.exceptions import AlreadyRemovedError
from messaging.models import Message
from messaging.exceptions import RemoveNotPermittedError



class MessagingTest(TestCase):
    def setUp(self):
        self.root = User.objects.create(
            username='root',
            is_staff=True,
            is_superuser=True,
        )
        self.user = User.objects.create(
            username='user',
        )
        self.user2 = User.objects.create(
            username='user2',
        )

    def test_removing(self):
        """Check removing messages"""
        msg = Message.objects.create(
            title='123', content='123',
            sender=self.root,
            receiver=self.user,
        )
        self.assertEqual(msg.is_removed(self.root), False)
        msg.remove(self.root)
        self.assertEqual(msg.is_removed(self.root), True)
        with self.assertRaises(AlreadyRemovedError):
            msg.remove(self.root)
        msg.remove(self.user)
        self.assertEqual(msg.is_removed(self.user), True)
        self.assertEqual(msg.is_removed(self.root), True)
        with self.assertRaises(RemoveNotPermittedError):
            msg.remove(self.user2)
        msg2 = Message.objects.create(
            title='123', content='123',
            sender=self.root,
            receiver=self.user,
        )   
        msg2.remove(self.user)
        self.assertEqual(msg2.is_removed(self.root), False)
        self.assertEqual(msg2.is_removed(self.user), True)
