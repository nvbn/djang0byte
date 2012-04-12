import json
from django.contrib.auth.models import User
from django.test import TestCase
from main.forms import (
    CreateBlogForm, CreatePostForm,
    CreateAnswerForm, EditPostForm,
    EditDraftForm, PostOptions,
)
from main.models import Profile, Post, Answer, BlogType, Blog, UserInBlog, Draft
from django.conf import settings


class PostTest(TestCase):
    def setUp(self):
        self.user = User.objects.create(username='test')
        Profile.objects.create(user=self.user)

    def test_create_blog(self):
        BlogType.objects.create(name=settings.DEFAULT_BLOG_TYPE)
        form = CreateBlogForm(self.user, {
            'name': 'okok',
            'description': 'test blog'
        })
        self.assertTrue(form.is_valid(), msg='blog form not work')
        blog = form.save()
        self.assertIsNotNone(blog.id, msg='blog saving not work')
        self.assertEqual(blog.name, 'okok', msg='blog data broken')

    def test_create_simple_post(self):
        form = CreatePostForm(self.user, {
            'type': Post.TYPE_POST,
            'title': 'OKOK!',
            'text': 'good',
            'raw_tags': 'op, ko, lot',
        })
        self.assertTrue(form.is_valid(), msg='simple post without blog validation failed')
        form.is_valid()
        post = form.save()
        self.assertIsNotNone(post.id, msg='simple post saving not work')
        self.assertEqual('OKOK!', post.title, msg='post data broken')
        self.assertEqual(Post.TYPE_POST, post.type, msg='post data broken')

    def test_create_link_post(self):
        form = CreatePostForm(self.user, {
            'type': Post.TYPE_LINK,
            'title': 'okok',
            'text': 'ok',
            'addition': 'http://welinux.ru',
        })
        self.assertTrue(form.is_valid(), msg='link post validation failed')
        form.is_valid()
        post = form.save()
        self.assertIsNotNone(post.id, msg='link post saving not work')
        self.assertEqual(post.addition, 'http://welinux.ru', msg='post data broken')

    def test_create_trans_post(self):
        form = CreatePostForm(self.user, {
            'type': Post.TYPE_TRANSLATE,
            'title': 'okok',
            'text': 'ok',
            'addition': 'http://welinux.ru',
        })
        self.assertTrue(form.is_valid(), msg='trans post validation failed')
        post = form.save()
        self.assertIsNotNone(post.id, msg='trans post saving not work')
        self.assertEqual(post.addition, 'http://welinux.ru', msg='trans post data broken')

    def test_create_answer_post(self):
        form = CreateAnswerForm(self.user, {
            'type': Post.TYPE_ANSWER,
            'title': 'okok',
            'answers': json.dumps(['ok', 'no', 'five']),
        })
        self.assertTrue(form.is_valid(), msg='answer validation failed')
        post = form.save()
        self.assertIsNotNone(post.id, msg='answer post saving not work')
        self.assertEqual(
            Answer.objects.filter(post=post).count(), 3,
            msg='answer creation failed'
        )

    def test_create_post_with_blog(self):
        BlogType.objects.create(name=settings.DEFAULT_BLOG_TYPE)
        blog = Blog.objects.create(name='okok', owner=self.user)
        UserInBlog.objects.create(blog=blog, user=self.user)
        form = CreatePostForm(self.user, {
            'type': Post.TYPE_POST,
            'title': 'okok',
            'text': 'okokok',
            'blog': blog.id,
        })
        self.assertTrue(form.is_valid(), msg='post with blog validation failed')
        post = form.save()
        self.assertIsNotNone(post.id, msg='post with blog saving not work')
        self.assertEqual(post.blog, blog, msg='blog not assigned')

    def test_edit_post(self):
        post = Post.objects.create(
            type=Post.TYPE_POST,
            title='okok',
            text='okokok',
            author=self.user,
        )
        form = EditPostForm(self.user, {
            'title': 'eeee',
            'text': '232323',
        }, instance=post)
        self.assertTrue(form.is_valid(), msg='edit post validation failed')
        changed_post = form.save()
        self.assertEqual(post.id, changed_post.id, msg='new post created')
        self.assertEqual(changed_post.title, 'eeee', msg='edit failed')

    def test_create_draft(self):
        form = EditDraftForm(self.user, {
            'type': Post.TYPE_POST,
        })
        self.assertTrue(form.is_valid(), msg='draft validation failed')
        draft = form.save()
        self.assertIsNotNone(draft.id, msg='draft saving not work')

    def test_edit_draft(self):
        draft = Draft.objects.create(
            title='okok',
            author=self.user,
            type=Post.TYPE_POST,
        )
        form = EditDraftForm(self.user, {
            'title': 'yee',
            'text': 'okok',
        }, instance=draft)
        form.is_valid()
        self.assertTrue(form.is_valid(), msg='edit draft validation failed')
        changed_draft = form.save()
        self.assertEqual(draft.id, changed_draft.id, msg='new draft created')
        self.assertEqual(changed_draft.title, 'yee', msg='draft edit failed')

    def text_draft_to_post(self):
        draft = Draft.objects.create(
            title='okok',
            author=self.user,
            type=Post.TYPE_POST,
        )
        form = CreatePostForm(self.user, draft.to_form_data())
        self.assertTrue(form.is_valid(), msg='convert draft to post validation failed')
        post = form.save()
        draft.delete()
        self.assertIsNotNone(post.id, msg='converted post saving failed')
        self.assertEqual(post.title, 'okok', msg='post from draft data broken')

    def test_joining(self):
        BlogType.objects.create(name=settings.DEFAULT_BLOG_TYPE)
        blog = Blog.objects.create(name='okok', owner=self.user)
        new_user = User.objects.create(username='ok12')
        self.assertTrue(blog.add_or_remove_user(new_user), msg='joining not work')
        self.assertEqual(UserInBlog.objects.filter(
            user=new_user, blog=blog,
        ).count(), 1, msg='joining not saved to db')
        self.assertFalse(blog.add_or_remove_user(new_user), msg='withdrawing not work')
        self.assertEqual(UserInBlog.objects.filter(
            user=new_user, blog=blog,
        ).count(), 0, msg='withdrawing not saved to db')

    def test_post_options(self):
        post = Post.objects.create(
            author=self.user,
            title='okok',
            text='eeee',
        )
        form = PostOptions({
            'disable_rate': True,
            'disable_reply': False,
            'pinch': True,
        }, instance=post)
        self.assertTrue(form.is_valid(), msg='options validating')
        post = form.save()
        self.assertTrue(post.disable_rate, msg='test options')
