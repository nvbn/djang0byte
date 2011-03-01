#!/usr/bin/python
from HTMLParser import HTMLParseError
from htmllib import HTMLParser

import sys, os, MySQLdb
sys.path.append('/home/nvbn/work/djang0byte/')
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import main.models as ndb
import settings
from datetime import datetime
from django.db.utils import IntegrityError, DatabaseError
try:
    usr = ndb.User.objects.get(username='nvbn')
    pr = ndb.Profile()
    pr.user = usr
    pr.save()
    bt = ndb.BlogType()
    bt.name = 'main'
    bt.save()
except:
    pass
db= MySQLdb.connect(host='127.0.0.1', user='root', passwd='qazwsx',
                    db='welinux', charset = "utf8", use_unicode = True)
cursor = db.cursor()
cursor.execute('SELECT * FROM users WHERE name != "nvbn"')
for user in cursor.fetchall():
    try:
        new_user = ndb.User(username=user[1], email=user[2],
                            password='md5$$' + user[7])

        new_user.save()
        icq = len(user[3]) < 11 and user[3] or ''
        new_profile = ndb.Profile(user=new_user, icq=icq, jabber=user[4],
                                  site=user[5], about=user[10], rate=int(user[8])-int(user[9]),
                                  rate_count=int(user[8])+int(user[9]), hide_mail=bool(user[14]),
                                  reply_post=bool(user[17]), reply_comment=bool(user[18]),
                                  posts_rate=int(user[20]), comments_rate=int(user[21]),
                                  blogs_rate=int(user[22]), reply_pm=bool(user[28]))
        if user[27]:
            try:
                city = ndb.City.objects.get(name=user[27])
            except ndb.City.DoesNotExist:
                city = ndb.City(name=user[27])
                city.save()
            new_profile.city = city
        new_profile.save()
    except IntegrityError, Warning:
        pass

for user in cursor.fetchall():
    profile = ndb.User.objects.get(name=user[1]).getProfile()
    for name in user[12].split(','):
        if name:
            friend = ndb.User.objects.get(name=name)
            ndb.Friends(friend=friend, user=profile).save()

cursor.execute('SELECT * FROM blogs')
blog_type = ndb.BlogType.objects.get(name=settings.DEFAULT_BLOG_TYPE)
for blog in cursor.fetchall():
    try:
        try:
            user = ndb.User.objects.get(username=blog[2])
        except ndb.User.DoesNotExist:
            user = ndb.User.objects.get(username='nvbn')

        new_blog = ndb.Blog(id=blog[0], name=blog[1], owner=user,
                            description=blog[6], type=blog_type,
                            rate=int(blog[3])-int(blog[4]), rate_count=int(blog[4])+int(blog[3]))
        new_blog.save()
    except:
        pass
cursor.execute('SELECT * FROM post')
for post in cursor.fetchall():
    try:
        try:
            author = ndb.User.objects.get(username=post[4])
        except ndb.User.DoesNotExist:
            author =  ndb.User.objects.get(username='nvbn')
        try:
            blog = ndb.Blog.objects.filter(name=post[8])[0]
        except IndexError:
            blog = False

        new_post = ndb.Post(author=author, title=post[2], preview=post[3],
                            text=post[7], id=post[0],
                            rate=int(post[5])-int(post[6]), rate_count=int(post[5])+int(post[6]))

        if blog:
            new_post.blog = blog
        new_post.save()
        new_post.date = datetime.fromtimestamp(float(post[1]))
        new_post.save()
        new_post.set_tags(post[10])
        new_post.create_comment_root()
    except IntegrityError:
        pass

cursor.execute("SELECT * FROM comment ORDER BY lvl")
comment_tmp = {}
for comment in cursor.fetchall():
    try:
        user = ndb.User.objects.get(username=comment[3])
        if comment[7] == 0:
            root = ndb.Comment.objects.filter(post=ndb.Post.objects.get(id=comment[4]), depth=1)[0]
        else:
            root = ndb.Comment.objects.get(id=comment_tmp[comment[4]])
        new_comment = root.add_child(post=ndb.Post.objects.get(id=comment[8]),
                                     author=user, rate=int(comment[5])-int(comment[6]),
                                     rate_count=int(comment[5])+int(comment[6]),
                                     text=comment[2], created=datetime.fromtimestamp(float(comment[1])))
        comment_tmp[int(comment[0])] = new_comment.id
    except (IntegrityError, KeyError, IndexError, ndb.User.DoesNotExist, HTMLParseError, AttributeError):
        pass

