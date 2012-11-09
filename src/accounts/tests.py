from django.test import TestCase
from django.contrib.auth.models import User
from accounts.remote_services import get_service
from blogging.models import Blog, Post, Comment
from accounts.models import BLOG_RATE, POST_RATE, COMMENT_RATE


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


class AccountTest(TestCase):
    def setUp(self):
        self.root = User.objects.create(
            username='root',
            is_staff=True,
            is_superuser=True,
        )

    def test_rates(self):
        blog_rate = 23
        blog = Blog.objects.create(
            name='blog', description='description',
            author=self.root, rate=blog_rate,
        )
        post_rate = 17
        post = Post.objects.create(
            title='asd', preview='fsd',
            content='esd', author=self.root,
            rate=post_rate,
        )
        comment_rate = 71
        comment = Comment.objects.create(
            post=post, author=self.root,
            content='asdfg', rate=comment_rate,
        )
        self.root.update_rate()
        self.assertEqual(self.root.rate, 
            BLOG_RATE * blog_rate + POST_RATE * post_rate + \
            COMMENT_RATE * comment_rate,
        )
