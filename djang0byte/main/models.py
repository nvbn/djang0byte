# -*- coding: utf-8 -*-
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.



from treebeard.ns_tree import NS_Node
from django.contrib.auth.models import User
from django.db import models
import datetime
import tagging
from tagging.fields import TagField
from tagging.models import Tag
from timezones.fields import TimeZoneField
from settings import TIME_ZONE, VALID_TAGS, VALID_ATTRS, NEWPOST_RATE, NEWBLOG_RATE, NEWCOMMENT_RATE, RATEPOST_RATE
from settings import RATECOM_RATE, RATEUSER_RATE, POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT
from utils import file_upload_path, Access
from parser import utils
from django.utils.translation import gettext as _
import parser.utils
from urlparse import urlparse

class BlogType(models.Model):
    """Types of blog"""
    name = models.CharField(max_length=30, verbose_name=_('Name'))
    display_default = models.BooleanField(default=True, verbose_name=_('Display in "all"?'))

    @staticmethod
    def check(name):
        """Check for exist

        Keyword arguments:
        name -- String

        Returns: Boolean

        """
        try:
            bt = BlogType.objects.get(name=name)
            return(True)
        except BlogType.DoesNotExist:
            return(False)

    def getBlogs(self):
        """Return blogs in type"""
        return(Blog.objects.filter(type=self))

    def __unicode__(self):
        """Return self name"""
        return(self.name)

    class Meta:
        verbose_name = _("Blog type")
        verbose_name_plural = _("Blogs types")


class Blog(models.Model):
    """Blog entrys"""
    name = models.CharField(max_length=30, verbose_name=_('Blog name'))
    owner = models.ForeignKey(User, verbose_name=_('Owner of blog'))
    description = models.TextField(verbose_name=_('Blog description'))
    rate = models.IntegerField(default=0, verbose_name=_('Blog rate'))
    rate_count = models.IntegerField(default=0, verbose_name=_('Count of raters'))
    type = models.ForeignKey(BlogType, verbose_name=_('Blog type'))
    default = models.BooleanField(default=False, verbose_name=_('Does not need join?'))

    
    def getUsers(self):
        """Get users in this blog"""
        return UserInBlog.objects.select_related('user').filter(blog=self)
    
    def checkUser(self, user):
        """Check user in blog
        
        Keyword arguments:
        user -- User
        
        Returns: Boolean
        
        """
        try:
            userInBlog = UserInBlog.objects.get(user=user, blog=self)
            return(True)
        except UserInBlog.DoesNotExist:
            return(False)
        
    def getPosts(self):
        """Get posts in blog"""
        return Post.objects.filter(blog=self)
        
    def rateBlog(self, user, value):
        """Rate blog
        
        Keyword arguments:
        user -- User
        value -- Integer
        
        Returns: Boolean
        
        """
        try:
            br = BlogRate.objects.get(blog=self, user=user)
            return(False)
        except BlogRate.DoesNotExist:
            self.rate += value
            self.rate_count += 1
            rate = BlogRate()
            rate.blog = self
            rate.user = user
            rate.save()
            user = Profile.objects.get(user=self.user)
            user.blogs_rate += 1
            user.save()
            return(True)
                
    def addOrRemoveUser(self, user):
        """add or remove user from blog
        
        Keyword arguments:
        user -- User
        
        Returns: None
        
        """
        if self.checkUser(user):
            UserInBlog.objects.get(user=user).delete()
        else:
            uib = UserInBlog()
            uib.blog = self
            uib.user = user
            uib.save()
                
    def __unicode__(self):
        """Return blog name"""
        return self.name

    class Meta:
        verbose_name = _("Blog")
        verbose_name_plural = _("Blogs")


class City(models.Model):
    """All of cities"""
    name = models.CharField(max_length=60, verbose_name=_('Name of city'))

    def __unicode__(self):
        """Return name"""
        return self.name

    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")

    
class Post(models.Model):
    """Posts table"""

    POST_TYPE = (
                 (0, 'Post'),
                 (1, 'Link'),
                 (2, 'Translate'),
                 (3, 'Answer'),
                 (4, 'Multiple Answer')
                 )

    author = models.ForeignKey(User, verbose_name=_('Author'))
    date = models.DateTimeField(auto_now=True, editable=False, verbose_name=_('Date'))
    blog = models.ForeignKey(Blog, blank=True, null=True, verbose_name=_('Blog'))
    title = models.CharField(max_length=300, verbose_name=_('Post title'))
    preview = models.TextField(blank=True, verbose_name=_('Preview text'))
    text = models.TextField(blank=True, verbose_name=_('Main text'))
    rate = models.IntegerField(default=0, verbose_name=_('Post rate'))
    rate_count = models.IntegerField(default=0, verbose_name=_('Count of raters'))
    type = models.IntegerField(choices=POST_TYPE, default=0, verbose_name=_('Type of post'))
    adittion = models.CharField(max_length=300, blank=True, verbose_name=_('Adittion field'))
    tags = TagField(verbose_name=_('Tags'))

    class Meta:
        ordering = ('-id', )

    def getComment(self):
        """Return first level comments in post"""
        try:
            comments = Comment.objects.filter(post=self, depth=1)[0]
            return comments.get_descendants()
        except IndexError:
            return(None)

    def setBlog(self, blog):
        """Set blog to post
        
        Keyword arguments:
        blog -- Blog
        
        Returns: Blog
        
        """
        if int(blog) == 0:
            self.blog = None
        else:
            self.blog = Blog.objects.get(id=blog)
            if self.blog.default or not self.blog.checkUser(self.author):
                 self.blog = None

        return(self.blog)
	  
    def createCommentRoot(self):
        """Create comment root for post"""
        comment_root = Comment.add_root(post=self, created=datetime.datetime.now())
        return(comment_root)
        
    def _getContent(self, type=0):
        """Return post content, 0 - preview, 1 - post
        
        Keyword arguments:
        type -- Integer
        
        Returns: Text
        
        """
        if self.type > 2:
            return Answer.objects.filter(post=self)
        elif type == 0:
            return(self.preview)
        else:
            return(self.text)
	  
    def getContent(self, type=0):
        """_getContent wrapper
        
        Keyword arguments:
        type -- Integer
        
        Returns: Text
        
        """
        return self._getContent(type)
	  
    def getFullContent(self, type=1):
        """Return preview
        
        Keyword arguments:
        type -- Integer
        
        Returns: Text
        
        """
        return self._getContent(1)
	  
    def ratePost(self, user, value):
        """Rate post
        
        Keyword arguments:
        user -- User
        value -- Integer
        
        Returns: Integer
        
        """
        try:
            pr = PostRate.objects.get(post=self, user=user)
            return(False)
        except PostRate.DoesNotExist:
            self.rate = self.rate + value
            self.rate_count = self.rate_count + 1
            self.save()
            rate = PostRate()
            rate.post = self
            rate.user = user
            rate.save()
            return(True)
            
    def getTags(self):
        """Return post tags"""
        return Tag.objects.get_for_object(self)
    
    def setTags(self, tag_list):
        """Set tags for post
        
        Keyword arguments:
        tag_list -- Tag
        
        Returns: None
        
        """
        Tag.objects.update_tags(self, tag_list)
        
        
    def save(self):
        """Parse html and save"""
        if self.type < 3:
            self.preview, self.text = utils.cut(self.text)
            utils.parse(self.preview, VALID_TAGS, VALID_ATTRS)
            utils.parse(self.text, VALID_TAGS, VALID_ATTRS)
        super(Post, self).save() # Call the "real" save() method
        
    def __unicode__(self):
        """Return post title"""
        return(self.title)

    class Meta:
        verbose_name = _("Post")
        verbose_name_plural = _("Posts")
 
    
class Comment(NS_Node):
    """Comments table"""
    post = models.ForeignKey(Post, verbose_name=_('Post'))
    author = models.ForeignKey(User, null=True, blank=True, verbose_name=_('Author'))
    text = models.TextField(blank=True, verbose_name=_('Text'))
    rate = models.IntegerField(default=0, verbose_name=_('Comment rate'))
    rate_count = models.IntegerField(default=0, verbose_name=_('Count of raters'))
    
    # Exception Value: Cannot use None as a query value
    created = models.DateTimeField(editable=False, verbose_name=_('Creation date'))
    
    
    node_order_by = ['created']
    
    def __unicode__(self):
        """Return comment content"""
        return self.text
    
    def save(self):
        """Parse html and save"""
        utils.parse(self.text, VALID_TAGS, VALID_ATTRS)
        super(Comment, self).save() # Call the "real" save() method
    
    @models.permalink
    def get_absolute_url(self):
        return ('node-view', ('ns', str(self.id), ))
    
    def getMargin(self):
        return (self.depth - 2) * 20
    
    class Meta:
        ordering = ['id']
        
    def rateComment(self, user, value):
        """Rate Comment
        
        Keyword arguments:
        user -- User
        value -- Integer
        
        Returns: Boolean
        
        """
        try:
            cr = CommentRate.objects.get(comment=self, user=user)
            return(False)
        except CommentRate.DoesNotExist:
            self.rate += value
            self.rate_count += 1
            rate = ComentRate()
            rate.comment = self
            rate.user = user
            rate.save()
            user = Profile.objects.get(user=self.user)
            user.comments_rate += 1
            user.save()
            return(True)

    class Meta:
        verbose_name = _("Comment")
        verbose_name_plural = _("Comments")


class UserInBlog(models.Model):
    """Compared list of users and blogs"""
    user = models.ForeignKey(User)
    blog = models.ForeignKey(Blog)

    def __unicode__(self):
        return self.blog.name

    def getId(self):
        return self.blog.id

    class Meta:
        verbose_name = _("User in blog list")
        verbose_name_plural = _("Users in blogs list")


class BlogWithUser(UserInBlog):
    """Abstract class"""
    def __unicode__(self):
        return self.parent.user.username

    class Meta:
        abstract = True


class Profile(models.Model):
    """User profile"""
    user = models.ForeignKey(User, unique=True, verbose_name=_('User'))
    city = models.ForeignKey(City, blank=True, null=True, verbose_name=_('City'))
    icq = models.CharField(max_length=10, blank=True, verbose_name=_('Icq'))
    jabber = models.CharField(max_length=60, blank=True, verbose_name=_('Jabber'))
    site = models.URLField(blank=True, verbose_name=_('Web site'))
    rate = models.IntegerField(default=0, verbose_name=_('Personal rate'))
    rate_count = models.IntegerField(default=0, verbose_name=_('Count of raters'))
    posts_rate = models.IntegerField(default=0, verbose_name=_('Rate earned by posts'))
    comments_rate = models.IntegerField(default=0, verbose_name=_('Rate earned by comments'))
    blogs_rate = models.IntegerField(default=0, verbose_name=_('Rate earned by blogs'))
    timezone = TimeZoneField(default=TIME_ZONE, verbose_name=_('Timezone'))
    avatar = models.ImageField(upload_to=file_upload_path, blank=True, null=True, verbose_name=_('User picture'))
    hide_mail = models.BooleanField(default=True, verbose_name=_('Show email?'))
    reply_post = models.BooleanField(default=True, verbose_name=_('Send notify about reply to post?'))
    reply_comment = models.BooleanField(default=True, verbose_name=_('Send notify about reply to comment?'))
    reply_pm = models.BooleanField(default=True, verbose_name=_('Send notify about PM?'))
    about = models.TextField(blank=True, verbose_name=_('About'))
    other = models.TextField(blank=True, verbose_name=_('Field for adittion'))
    
    def getPosts(self):
        """Get posts by user"""
        return Post.objects.filter(author=self.user)
        
    def getFriends(self):
        """Get user friends"""
        return Friends.objects.select_related('friend').filter(user=self)

    def getBlogs(self):
        """Get blogs contain it"""
        return UserInBlog.objects.select_related('blog').filter(user=self.user)
        
    def rateUser(self, user, value):
        """Rate user
        
        Keyword arguments:
        user -- User
        value -- Integer
        
        Returns: Integer
        
        """
        if not UserRate.objects.get(user=self):
            self.rate += value
            self.rate_count += 1
            rate = UserRate()
            rate.profile = self
            rate.user = user
            rate.save()
            return(True)
        else:
            return(False)

    def getRate(self):
        """Get user rate"""
        return(self.rate + self.posts_rate * POST_RATE_COEFFICIENT
               + self.blogs_rate * BLOG_RATE_COEFFICIENT
               + self.comments_rate * COMMENT_RATE_COEFFICIENT)

    def checkAccess(self, type):
        """Check user access

        Keyword arguments:
        type -- Access:

        Returns: Boolean

        """
        rate = self.getRate()
        if type == Access.newBlog and rate >= NEWBLOG_RATE:
            return(True)
        elif type == Access.newComment and rate >= NEWCOMMENT_RATE:
            return(True)
        elif type == Access.newPost and rate >= NEWPOST_RATE:
            return(True)
        elif type == Access.rateComment and rate >= RATECOM_RATE:
            return(True)
        elif type == Access.rateBlog and rate >= RATEBLOG_RATE:
            return(True)
        elif type == Access.ratePost and rate >= RATEPOST_RATE:
            return(True)
        elif type == Access.rateUser and rate >= RATEUSER_RATE:
            return(True)
        else:
            return(False)

    def __unicode__(self):
        """Return username"""
        return self.user.username

    class Meta:
        verbose_name = _("User profile")
        verbose_name_plural = _("User profiles")


class Friends(models.Model):
    """Friends table"""
    friend = models.ForeignKey(User, verbose_name=_('Friend'))
    user = models.ForeignKey(Profile, verbose_name=_('User'))

    class Meta:
        verbose_name = _("Friend")
        verbose_name_plural = _("Friends")


class Answer(models.Model):
    """Answers class"""
    post = models.ForeignKey(Post, verbose_name=_('Post'))
    count = models.IntegerField(default=0, verbose_name=_('Count of choose'))
    value = models.TextField(verbose_name=_('Answer variant'))
    
    def fix(self, user):
        """Fixate votes and block next vote
        
        Keyword arguments:
        user -- User
        
        Returns: None
        
        """
        vote = AnswerVote()
        vote.answer = self.post
        vote.user = user
        vote.save()
    
    def _vote(self, user, multiple=False):
        """Vote to answer
        
        Keyword arguments:
        user -- User
        multiple -- Boolean
        
        Returns: Boolean
        
        """
        if multiple == False:
            self.fix(user)
        self.count = self.count + 1
        self.save()
        
    @staticmethod
    def check(post, user):
        """Check vote access
        
        Keyword arguments:
        post -- Post
        user -- User
        
        Returns: Boolean
        
        """
        try:
            vote = AnswerVote.objects.filter(answer=post, user=user)[0]     
            return(False)
        except 	IndexError:
            return(True)
	    
    def vote(self, user, multiple=False):
        """Vote to answer
        
        Keyword arguments:
        user -- User
        multiple -- Boolean
        
        Returns: Boolean
        
        """
        if Answer.check(self.post, user) or multiple:
            self._vote(user)
            return(True)
        else:
            return(False)
            
    def __unicode__(self):
        """Return value"""
        return(self.value)

    class Meta:
        verbose_name = _("Answer variant")
        verbose_name_plural = _("Answers variants")

	    
class AnswerVote(models.Model):
    """Votes for answer"""
    answer = models.ForeignKey(Post, verbose_name=_('Answer'))
    user = models.ForeignKey(User, verbose_name=_('User'))

    class Meta:
        verbose_name = _("Vote to answer log")
        verbose_name_plural = _("Answers votes log")
    
class Favourite(models.Model):
    """Favourite posts table"""
    post = models.ForeignKey(Post, verbose_name=_('Post'))
    user = models.ForeignKey(User, verbose_name=_('User'))

    class Meta:
        verbose_name = _("Favourite post")
        verbose_name_plural = _("Favourite posts")


class Spy(models.Model):
    """Spyed posts table"""
    post = models.ForeignKey(Post, verbose_name=_('Post'))
    user = models.ForeignKey(User, verbose_name=_('User'))

    class Meta:
        verbose_name = _("Post spying")
        verbose_name_plural = _("Post spyings")


class PostRate(models.Model):
    """Post rates"""
    post = models.ForeignKey(Post, verbose_name=_('Post'))
    user = models.ForeignKey(User, verbose_name=_('User'))

    class Meta:
        verbose_name = _("Post rate log")
        verbose_name_plural = _("Post rates log")

    
class CommentRate(models.Model):
    """Comment rates"""
    comment = models.ForeignKey(Comment, verbose_name=_('Comment'))
    user = models.ForeignKey(User, verbose_name=_('User'))

    class Meta:
        verbose_name = _("Comment rate log")
        verbose_name_plural = _("Comment rates log")


class BlogRate(models.Model):
    """Blog rates"""
    blog = models.ForeignKey(Blog, verbose_name=_('Blog'))
    user = models.ForeignKey(User, verbose_name=_('User'))

    class Meta:
        verbose_name = _("Blog rate log")
        verbose_name_plural = _("Blog rates log")


class UserRate(models.Model):
    """User rates"""
    profile = models.ForeignKey(Profile, verbose_name=_('Profile'))#voted
    user = models.ForeignKey(User, verbose_name=_('User'))#who vote

    class Meta:
        verbose_name = _("User rate log")
        verbose_name_plural = _("User rates log")


class Notify(models.Model):
    """Class contain notifys for 'lenta'"""
    user = models.ForeignKey(User, verbose_name=_('User'))
    post = models.ForeignKey(Post, verbose_name=_('Post'), blank=True, null=True)
    comment = models.ForeignKey(Comment, verbose_name=_('Comment'), blank=True, null=True)
    
    @classmethod
    def newNotify(self, is_post, alien, user):
        """Create notify
        
        Keyword arguments:
        is_post -- Boolean
        alien -- Post or Comment
        user - User
        
        Returns: Notify
        
        """
        self = Notify()
        self.user = user
        if is_post:
            self.post = alien
        else:
            self.comment = alien
        self.save()
        return(self)
            
    @staticmethod
    def newPostNotify(post):
        """Notify for new post
        
        Keyword arguments:
        post -- Post
        
        Returns: None
        
        """
        users = list(Profile.objects.get(user=post.author).getFriends())
        users = [user.friend for user in users]
        if post.blog != None:
            users += [blog_user.user for blog_user in post.blog.getUsers()]
        d = {}
        for x in users:
            if x != post.author: 
                d[x]=x
        users = d.values()
        for user in users:
            Notify.newNotify(True, post, user)
    
    @staticmethod
    def newCommentNotify(comment):
        """Notify for new comment
        
        Keyword arguments:
        comment -- Comment
        
        Returns: None
        
        """
        if comment.depth == 2:
            Notify.newNotify(False, comment, comment.post.author)
            spy = Spy.objects.select_related('user').filter(post=comment.post)
            try:
                for spy_elem in Spy:
                    Notify.newNotify(False, comment, spy_elem.user)
            except TypeError:
                pass
        else:
            Notify.newNotify(False, comment, comment.get_parent().author)
            
    def getType(self):
        """Return notify type"""
        if self.post != None:
            return('post')
        else:
            return('comment')

    def __unicode__(self):
        """Return notify description"""
        if self.post != None:
            return("post %s -- %s" % (self.post, self.user))
        else:
            return("comment %s -- %s" % (self.comment, self.user))

    class Meta:
        verbose_name = _("Notify")
        verbose_name_plural = _("Notify messages")


class TextPage(models.Model):
    """Page contain a text"""
    url = models.CharField(verbose_name=_('Page url'), max_length=30)
    name = models.CharField(verbose_name=_('Page name'), max_length=30)
    content = models.TextField(verbose_name=_('Content'), blank=True)

    class Meta:
        verbose_name = _("Page")
        verbose_name_plural = _("Text pages")

    def __unicode__(self):
        """Get page content

        Keyword arguments:
        self -- TextPage

        Returns: String

        """
        return(self.name)


class MeOn(models.Model):
    """User on other site record"""
    url = models.URLField(verbose_name=_("Page url"))
    title = models.CharField(verbose_name=_("Title"), max_length=30)
    user = models.ForeignKey(User, verbose_name=_("User"))

    def _is_statused(self):
        """Match url for statused service"""
        parsed = urlparse(self.url)
        for name in Statused.SERVICE_TYPE:
            if name[1] in parsed.netloc.split('.'):
                return({'service': name[0], 'username': parsed.path.split('/')[1]})

    def parse(self):
        """Check type and save"""
        type = self._is_statused()
        if 'http' not in self.url:
            self.url = 'http://' + self.url
        if len(type) == 2:
            service = Statused()
            service.url = self.url
            service.title = self.title
            service.type = type['service']
            service.name = type['username']
            service.save()
            return(True)
        else:
            return(False)

    class Meta:
        verbose_name = _("User on other site")
        verbose_name_plural = _("Users on other sites")

class Statused(MeOn):
    """Service with status users"""

    SERVICE_TYPE = (
        (0, 'lastfm'),
        (1, 'twitter'),
        (2, 'juick')
    )

    show = models.BooleanField(default=True)
    type = models.IntegerField(choices=SERVICE_TYPE, default=0, verbose_name=_('Name of service'))
    name = models.CharField(max_length=30, verbose_name=_('User name in service'))

    def get_status(self):
        """Get status"""
        pass

