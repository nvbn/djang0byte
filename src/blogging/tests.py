from django.test import TestCase
from django.contrib.auth.models import User
from tools.exceptions import (
    AlreadyRatedError, InvalidRateSignError,
    RateDisabledError,
)
from blogging.models import Blog, Post, Quiz, Answer
from blogging.exceptions import (
    AlreadySubscribedError, NotSubscribedError,
    AlreadyStarredError, NotStarredError,
    AlreadyAnsweredError, NotSeveralQuizError,
    AlreadyIgnoredError, VoteForIgnoredError,
    IgnoreForVotedError,
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

    def test_vote_quiz(self):
        """Test vote for quiz"""
        post = Post.objects.create(
            title='asd', preview='fsd',
            content='esd',
        )
        quiz = Quiz.objects.create(
            name='qqqq', is_several=False,
            post=post,
        )
        answer = Answer.objects.create(
            name='answer', quiz=quiz,
        )
        answer1 = Answer.objects.create(
            name='answer1', quiz=quiz,
        )
        self.assertEqual(quiz.is_voted(self.root), False)
        with self.assertRaises(NotSeveralQuizError):
            quiz.vote(self.root, [answer, answer1])
        quiz.vote(self.root, answer)
        self.assertEqual(quiz.is_voted(self.root), True)
        with self.assertRaises(AlreadyAnsweredError):
            quiz.vote(self.root, answer1)
        with self.assertRaises(IgnoreForVotedError):
            quiz.ignore(self.root)

    def test_ignore_quiz(self):
        """Test ignore for quiz"""
        post = Post.objects.create(
            title='asd', preview='fsd',
            content='esd',
        )
        quiz = Quiz.objects.create(
            name='qqqq', is_several=False,
            post=post,
        )
        answer = Answer.objects.create(
            name='answer', quiz=quiz,
        )
        answer1 = Answer.objects.create(
            name='answer1', quiz=quiz,
        )
        self.assertEqual(quiz.is_ignored(self.root), False)
        quiz.ignore(self.root)
        self.assertEqual(quiz.is_ignored(self.root), True)
        with self.assertRaises(AlreadyIgnoredError):
            quiz.ignore(self.root)
        with self.assertRaises(VoteForIgnoredError):
            quiz.vote(self.root, answer)
