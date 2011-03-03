#!/usr/bin/python
import sys
sys.path.append('/home/nvbn/work/djang0byte/')

from HTMLParser import HTMLParseError
from htmllib import HTMLParser
import  os, MySQLdb

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
import main.models as ndb
import settings
from datetime import datetime
import memcache
mc = memcache.Client(['127.0.0.1:11211'], debug=0)
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
cursor.execute('SELECT COUNT(*) FROM users WHERE name != "nvbn"')
count = cursor.fetchall()[0][0]
mark = count / 20
f = mark
cursor.execute('SELECT * FROM users WHERE name != "nvbn"')
for user in cursor.fetchall():
    if not f:
        f = mark
        sys.stdout.write('#')
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
        if user[11]:
            new_profile.avatar = '/media/av/%s/' % (user[11])
        new_profile.save()
    except IntegrityError, Warning:
        pass
    f -= 1

print('users convereted')

for user in cursor.fetchall():
    profile = ndb.User.objects.get(name=user[1]).getProfile()
    for name in user[12].split(','):
        if name:
            friend = ndb.User.objects.get(name=name)
            ndb.Friends(friend=friend, user=profile).save()

print('friends converted')
cursor.execute('SELECT COUNT(*) FROM blogs')
count = cursor.fetchall()[0][0]
mark = count / 20
f = mark
cursor.execute('SELECT * FROM blogs')
blog_type = ndb.BlogType.objects.get(name=settings.DEFAULT_BLOG_TYPE)
for blog in cursor.fetchall():
    if not f:
        f = mark
        sys.stdout.write('#')
    try:
        try:
            user = ndb.User.objects.get(username=blog[2])
        except ndb.User.DoesNotExist:
            user = ndb.User.objects.get(username='nvbn')

        new_blog = ndb.Blog(id=blog[0], name=blog[1], owner=user,
                            description=blog[6], type=blog_type,
                            rate=int(blog[3])-int(blog[4]), rate_count=int(blog[4])+int(blog[3]))
        if blog[5]:
            new_blog.avatar = '/media/bl/%s/' % (blog[5])
        new_blog.save()
    except:
        pass
    f-=1

print('blogs converted')
cursor.execute('SELECT * FROM inblog')
for uib in cursor.fetchall():
    try:
        new_uib = ndb.UserInBlog(user=ndb.User.objects.get(username=uib[2]), blog=ndb.Blog.objects.get(id=uib[1]))
        new_uib.save()
    except (ndb.User.DoesNotExist, ndb.Blog.DoesNotExist):
        pass

print('users in blog converted')

cursor.execute('SELECT * FROM brate')
for brate in cursor.fetchall():
    try:
        blog_rate = ndb.BlogRate(blog=ndb.Blog.objects.get(id=brate[2]), user=ndb.User.objects.get(username=brate[1]))
        blog_rate.save()
    except (ndb.User.DoesNotExist, ndb.Blog.DoesNotExist):
        pass

print('blog rates converted')
cursor.execute('SELECT COUNT(*) FROM post')
count = cursor.fetchall()[0][0]
mark = count / 20
f = mark
cursor.execute('SELECT * FROM post')
for post in cursor.fetchall():
    if not f:
        f = mark
        sys.stdout.write('#')
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
                            text=post[7].replace('[','<').replace(']','>'), id=post[0],
                            rate=int(post[5])-int(post[6]), rate_count=int(post[5])+int(post[6]),
                            type=post[13])

        if blog:
            new_post.blog = blog
        new_post.save()
        new_post.date = datetime.fromtimestamp(float(post[1]))
        new_post.save(edit=False, convert=True)
        new_post.set_tags(post[10])
    except (IntegrityError, HTMLParseError, TypeError):
        pass
    f -= 1

print('posts converted')

cursor.execute("SELECT * FROM rate")
for rate in cursor.fetchall():
    try:
        post_rate = ndb.PostRate(user=ndb.User.objects.get(username=rate[1]), post=ndb.Post.objects.get(id=rate[0]))
        post_rate.save()
    except (ndb.User.DoesNotExist, ndb.Post.DoesNotExist):
        pass

print('post rates converted')
cursor.execute('SELECT COUNT(*) FROM comment')
count = cursor.fetchall()[0][0]
mark = count / 20
f = mark
cursor.execute("SELECT * FROM comment ORDER BY lvl")

for comment in cursor.fetchall():
    if not f:
        f = mark
        sys.stdout.write('#')
    try:
        user = ndb.User.objects.get(username=comment[3])
        if comment[7] == 0:
            root = ndb.Comment.objects.filter(post=ndb.Post.objects.get(id=comment[4]), depth=1)[0]
        else:
            root = ndb.Comment.objects.get(id=int(mc.get(str(comment[4]))))
        new_comment = root.add_child(post=ndb.Post.objects.get(id=comment[8]),
                                     author=user, rate=int(comment[5])-int(comment[6]),
                                     rate_count=int(comment[5])+int(comment[6]),
                                     text=comment[2].replace('[','<').replace(']','>'), created=datetime.fromtimestamp(float(comment[1])))
        mc.set(str(comment[0]), new_comment.id)
    except (IntegrityError, KeyError, IndexError, ndb.User.DoesNotExist, ndb.Profile.DoesNotExist, HTMLParseError, AttributeError, ndb.Post.DoesNotExist, TypeError, ndb.Comment.DoesNotExist):
        pass
    f -= 1
print('comments converted')


cursor.execute("SELECT * FROM crate")
for rate in cursor.fetchall():
    try:
        cmnt_rate = ndb.CommentRate(user=ndb.User.objects.get(username=rate[1]), comment=ndb.Comment.objects.get(id=mc.get(str(rate[0]))))
        cmnt_rate.save()
    except (ndb.User.DoesNotExist, ndb.Comment.DoesNotExist):
        pass

print('comment rates converted')

cursor.execute("SELECT * FROM answ")
for answ in cursor.fetchall():
    try:
        answer = ndb.Answer(post=ndb.Post.objects.get(id=answ[1]), count=answ[3], value=answ[2])
        answer.save()
    except (ndb.Post.DoesNotExist, KeyError, IndexError, AttributeError):
        pass

print('answer converted')

cursor.execute("SELECT * FROM wansw")
for wansw in cursor.fetchall():
    try:
        vote = ndb.AnswerVote(answer=ndb.Post.objects.get(id=wansw[1]), user=ndb.User.objects.get(username=wansw[2]))
        vote.save()
    except (ndb.Post.DoesNotExist, KeyError, IndexError, AttributeError, ndb.User.DoesNotExist):
        pass

print('votes converted')

cursor.execute("SELECT * FROM favourite")
for fav in cursor.fetchall():
    try:
        favourite = ndb.Favourite(post=ndb.Post.objects.get(id=fav[1]), user=ndb.User.objects.get(username=fav[2]))
        favourite.save()
    except (ndb.Post.DoesNotExist, KeyError, IndexError, AttributeError, ndb.User.DoesNotExist):
        pass

print('favourite converted')

cursor.execute("SELECT * FROM eye")
for eye in cursor.fetchall():
    try:
        spy = ndb.Spy(user=ndb.User.objects.get(username=eye[2]), post=ndb.Post.objects.get(id=eye[1]))
        spy.save()
    except (ndb.Post.DoesNotExist, KeyError, IndexError, AttributeError, ndb.User.DoesNotExist):
        pass

print('spy converted')
