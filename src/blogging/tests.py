from django.test import TestCase
from django.contrib.auth.models import User
from tools.exceptions import (
    AlreadyRatedError, InvalidRateSignError,
    RateDisabledError,
)
from blogging.models import Blog, Post
from blogging.exceptions import (
    AlreadySubscribedError, NotSubscribedError,
    AlreadyStarredError, NotStarredError,
)


class BloggingTest(TestCase):
    def setUp(self):
        self.root = User.objects.create(
            username='root',
            is_staff=True,
            is_superuser=True,
        )

    def test_rating(self):
        """Check ratins"""
        blog = Blog.objects.create(
            name='blog', description='description',
            author=self.root,
        )
        self.assertEqual(blog.is_rated(self.root), False)
        with self.assertRaises(InvalidRateSignError):
            blog.set_rate(-15, self.root)
        blog.set_rate(+1, self.root)
        self.assertEqual(blog.is_rated(self.root), True)
        with self.assertRaises(AlreadyRatedError):
            blog.set_rate(-1, self.root)
        blog2 = Blog.objects.create(
            name='blog', description='description',
            author=self.root, is_rate_enabled=False,
        )
        with self.assertRaises(RateDisabledError):
            blog2.set_rate(-1, self.root)

    def test_subscriptions(self):
        """Check subscriptions"""
        post = Post.objects.create(
            title='asd', preview='fsd',
            content='esd',
        )
        self.assertEqual(post.is_subscribed(self.root), False)
        post.subscribe(self.root)
        self.assertEqual(post.is_subscribed(self.root), True)
        with self.assertRaises(AlreadySubscribedError):
            post.subscribe(self.root)
        post.unsubscribe(self.root)
        self.assertEqual(post.is_subscribed(self.root), False)
        with self.assertRaises(NotSubscribedError):
            post.unsubscribe(self.root)

    def test_stars(self):
        """Check stars"""
        post = Post.objects.create(
            title='asd', preview='fsd',
            content='esd',
        )
        self.assertEqual(post.is_starred(self.root), False)
        post.star(self.root)
        self.assertEqual(post.is_starred(self.root), True)
        with self.assertRaises(AlreadyStarredError):
            post.star(self.root)
        post.unstar(self.root)
        self.assertEqual(post.is_starred(self.root), False)
        with self.assertRaises(NotStarredError):
            post.unstar(self.root)
