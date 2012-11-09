from django.test import TestCase
from django.contrib.auth.models import User
from tools.exceptions import (
    AlreadyRatedError, InvalidRateSignError,
    RateDisabledError, AlreadyRemovedError,
    NotRemovedError,
)
from blogging.models import Blog, Post, Quiz, Answer, Comment
from blogging.exceptions import (
    AlreadySubscribedError, NotSubscribedError,
    AlreadyStarredError, NotStarredError,
    AlreadyAnsweredError, NotSeveralQuizError,
    AlreadyIgnoredError, VoteForIgnoredError,
    IgnoreForVotedError, NotQuestionError,
    SolutionAlreadyExistError, SoulutionDoesNotExistError,
    WrongSolutionHolderError,
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

    def test_removing(self):
        """Check removing"""
        post = Post.objects.create(
            title='asd', preview='fsd',
            content='esd', author=self.root,
        )
        self.assertEqual(post.is_removed, False)
        post.remove()
        self.assertEqual(post.is_removed, True)
        with self.assertRaises(AlreadyRemovedError):
            post.remove()

    def test_restore(self):
        """Check restoring"""
        post = Post.objects.create(
            title='asd', preview='fsd',
            content='esd', author=self.root,
        )
        with self.assertRaises(NotRemovedError):
            post.restore()
        post.remove()
        self.assertEqual(post.is_removed, True)
        post.restore()
        self.assertEqual(post.is_removed, False)

    def test_subscriptions(self):
        """Check subscriptions"""
        post = Post.objects.create(
            title='asd', preview='fsd',
            content='esd', author=self.root,
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
            content='esd', author=self.root,
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
            content='esd', author=self.root,
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
            content='esd', author=self.root,
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

    def test_solution(self):
        """Test question sulution"""
        post = Post.objects.create(
            title='asd', preview='fsd',
            content='esd', author=self.root,
        )
        comment = Comment.objects.create(
            post=post, author=self.root,
            content='asdfg',
        )
        with self.assertRaises(NotQuestionError):
            post.set_solution(comment)
        post.type = Post.TYPE_QUESTION
        with self.assertRaises(SoulutionDoesNotExistError):
            post.get_solution()
        self.assertEqual(post.has_solution(), False)
        post.set_solution(comment)
        self.assertEqual(post.has_solution(), True)
        self.assertEqual(post.get_solution(), comment)
        comment2 = Comment.objects.create(
            post=post, author=self.root,
            content='asdfg',
        )
        with self.assertRaises(SolutionAlreadyExistError):
            post.set_solution(comment2)
        post2 = Post.objects.create(
            title='asd', preview='fsd', author=self.root,
            content='esd', type=Post.TYPE_QUESTION, 
        )
        with self.assertRaises(WrongSolutionHolderError):
            post2.set_solution(comment2)

    def test_remove_solution(self):
        """Test remove solution"""
        post = Post.objects.create(
            title='asd', preview='fsd', author=self.root,
            content='esd', type=Post.TYPE_QUESTION,
        )
        comment = Comment.objects.create(
            post=post, author=self.root,
            content='asdfg',
        )
        with self.assertRaises(SoulutionDoesNotExistError):
            post.unset_solution()
        post.set_solution(comment)
        self.assertEqual(post.has_solution(), True)
        post.unset_solution()
        self.assertEqual(post.has_solution(), False)
