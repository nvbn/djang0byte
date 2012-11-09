from django.test import TestCase
from django.contrib.auth.models import User
from accounts.remote_services import get_service
from blogging.models import Blog, Post, Comment
from accounts.models import BLOG_RATE, POST_RATE, COMMENT_RATE
from accounts.exceptions import MergingNotAvailable
from accounts.forms import ChangeUserForm
import json


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


class ModelsTest(TestCase):
    def setUp(self):
        self.root = User.objects.create(
            username='root',
            is_staff=True,
            is_superuser=True,
        )

    def test_rates(self):
        """Check account rates"""
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

    def test_services(self):
        """Check services in json field"""
        self.root.services = {
            'welinux': 'http://welinux.ru/',
            'lastfm': 'http://www.lastfm.ru/user/nvbn',
        }
        self.root.save()
        self.assertEqual(len(self.root.services), 2)
        received = User.objects.get(id=self.root.id)
        self.assertEqual(len(self.root.services), 2)
        self.assertEqual(self.root.services['welinux'].description, None)
        self.assertGreater(self.root.services['lastfm'].description, 3)

    def test_merge(self):
        """Test profiles merging"""
        user = User.objects.create(
            username='user',
        )
        for author in [user, self.root] * 5:
            Blog.objects.create(
                name='blog', description='description',
                author=author,
            )
            post = Post.objects.create(
                title='asd', preview='fsd',
                content='esd', author=author,
            )
            Comment.objects.create(
                post=post, author=author,
                content='asdfg',
            )
        with self.assertRaises(MergingNotAvailable):
            self.root.merge('123')
        blog_count = Blog.objects.filter(author__in=(user, self.root)).count()
        post_count = Post.objects.filter(author__in=(user, self.root)).count()
        comment_count = Comment.objects.filter(author__in=(user, self.root)).count()
        key = user.create_merge_key()
        self.assertIsNotNone(key)
        self.root.merge(key)
        self.assertEqual(blog_count, Blog.objects.filter(author=self.root).count())
        self.assertEqual(post_count, Post.objects.filter(author=self.root).count())
        self.assertEqual(comment_count, Comment.objects.filter(author=self.root).count())


class FormsTest(TestCase):
    def setUp(self):
        self.root = User.objects.create(
            username='root',
            is_staff=True,
            is_superuser=True,
        )

    def test_change_user(self):
        """Test changing user"""
        form = ChangeUserForm({
            'first_name': '123',
            'last_name': '1235',
            'services': json.dumps({
                'welinux': 'http://welinux.ru/',
                'lastfm': 'http://www.lastfm.ru/user/nvbn',
            }),
        }, instance=self.root)
        self.assertEqual(form.is_valid(), True)
        user = form.save()
        self.assertEqual(user.first_name, '123')
        form = ChangeUserForm({
            'first_name': '123',
            'last_name': '1235',
            'services': json.dumps({
                'welinux': 'httpwelinux',
                'lastfm': 'http://www.lastfm.ru/user/nvbn',
            }),
        }, instance=self.root)
        self.assertEqual(form.is_valid(), False)
