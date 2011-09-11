# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand, CommandError
from main.models import Blog, BlogType, Comment, Post, Profile
from django.contrib.auth.models import User
from random import random
from functools import partial
from urllib import urlopen
from BeautifulSoup import BeautifulSoup
from datetime import datetime
from django.conf import settings
from treemenus.models import Menu

def obtain_spring(url):
    data = urlopen('http://vesna.yandex.ru/%s' % url).read()
    soup = BeautifulSoup(data)
    return (
        soup.find('h1').string[7:][:-2],
        ''.join(map(unicode, soup.find('h1').parent.findAll('p'))),
    )

class Command(BaseCommand):
    help = """
    --post-count default 100
    --comment-limit default 100 per post
    """

    def handle(self, **options):
        Menu.objects.get_or_create(
            name='menu'
        )
        Menu.objects.get_or_create(
            name='bottom_menu'
        )
        post_count = int(options.get('post-count', 100))
        comment_limit = int(options.get('comment-limit', 100))
        random_rate = lambda: int(random() * 1000)
        get_rand = lambda _list: _list[int(random()*len(_list))]
        blog_types = map(
            lambda type: BlogType.objects.get_or_create(name=type)[0],
            (getattr(settings, 'DEFAULT_BLOG_TYPE', 'main'), 'talks', 'personal',)
        )
        random_type = partial(get_rand, blog_types)
        users = map(
            lambda username: User.objects.get_or_create(username=username)[0],
            ('bob', 'paul', 'mike', 'anna', 'sasha', 'katya', 'masha',)
        )
        map(
            lambda user: Profile.objects.get_or_create(
                user=user,
                rate=random_rate(),
                posts_rate=random_rate(),
                comments_rate=random_rate(),
                blogs_rate=random_rate(),
            )[0], users
        )
        random_user = partial(get_rand, users)
        blogs = map(
            lambda (blog_name, url): Blog.objects.get_or_create(
                name=blog_name,
                owner=random_user(),
                type=random_type(),
                description=url,
                rate=random_rate(),
                rate_count=random_rate(),
            )[0], (
                (u'астрономии', 'astronomy.xml'),
                (u'геологии', 'geology.xml'),
                (u'гироскопии', 'gyroscope.xml'),
                (u'литературоведению', 'literature.xml'),
                (u'маркетингу', 'marketing.xml'),
                (u'математике', 'mathematics.xml'),
                (u'музыковедению', 'music.xml'),
                (u'политологии', 'polit.xml'),
                (u'почвоведению', 'agrobiologia.xml'),
                (u'правоведению', 'law.xml'),
                (u'психологии', 'psychology.xml'),
                (u'страноведению', 'geography.xml'),
                (u'физике', 'physics.xml'),
                (u'философии', 'philosophy.xml'),
                (u'химии', 'chemistry.xml'),
                (u'эстетике', 'estetica.xml'),
            )
        )
        random_blog = partial(get_rand, blogs)
        random_comment = lambda limit: Post.objects.all()[int(random() * limit)].title
        for counter in range(post_count):
            post = Post()
            post.author = random_user()
            post.blog = random_blog()
            post.title, post.text = obtain_spring(post.blog.description)
            post.rate = random_rate()
            post.rate_count = random_rate()
            post.save(edit=False, retry=True)
            post.set_tags(','.join(post.title.split()))
            last = root = post.create_comment_root()
            limit = int(random() * comment_limit)
            while limit:
                if not int(random()*3):
                    last = root
                last = last.add_child(
                    post=post,
                    author=random_user(),
                    text=random_comment(counter),
                    created=datetime.now(),
                    rate=random_rate(),
                    rate_count=random_rate()
                )
                limit -= 1

            
