# -*- coding: utf-8 -*-
from treebeard.ns_tree import NS_Node
from django.contrib.auth.models import User
from django.db import models
from _parser.models import _parser
import datetime


class Blog(models.Model):
    """Blog entrys"""
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(User)
    description = models.TextField()
    rate = models.IntegerField(null=True)
    rate_count = models.IntegerField(null=True)
    
    def getUsers(self):
        """Get users in this blog"""
        return UserInBlog.objects.filter(blog=self)
    
    def checkUser(self, user):
		"""Check user in blog"""
		try:
			userInBlog = UserInBlog.objects.get(user=user, blog=self)
			return(True)
		except UserInBlog.DoesNotExist:
			return(False)
        
    def getPosts(self):
        """Get posts in blog"""
        return Post.objects.filter(blog=self)
        
    def ratePost(self, user, value):
        """Rate user"""
        if not BlogRate.objects.get(blog=self, user=user):
	    self.rate += value
	    self.rate_count += 1
	    rate = BlogRate()
	    rate.blog = self
	    rate.user = user
	    rate.save()
	    return(True)
	else:
	    return(False)
        
    def __unicode__(self):
        """Return blog name"""
        return self.name

class Tag(models.Model):
    """Tags table"""
    name = models.CharField(max_length=30)
    
    def getPosts(self):
        """Get posts with tag"""
        posts = PostWithTag.objects.filter(tag=self)
	return posts

    def __unicode__(self):
        """Return tag name"""
        return self.name

class City(models.Model):
    """All of citys"""
    name = models.CharField(max_length=60)

    def __unicode__(self):
        """Return name"""
        return self.name

    
class Post(models.Model):
    """Posts table"""

    POST_TYPE=(
        (0, 'Post'),
        (1, 'Link'),
        (2, 'Translate'),
        (3, 'Answer'),
        (4, 'Multiple Answer')
    )

    author = models.ForeignKey(User)
    date = models.DateTimeField(auto_now=True,editable=False)
    blog = models.ForeignKey(Blog, blank=True, null=True)
    title = models.CharField(max_length=300)
    preview = models.TextField()
    text = models.TextField()
    rate = models.IntegerField(null=True)
    rate_count = models.IntegerField(null=True)
    type = models.IntegerField(choices=POST_TYPE, default=0)
    adittion = models.CharField(max_length=300, blank=True)

    class Meta:
        ordering = ('-id',)

    def getComment(self):
        """Return first level comments in post"""
        comments = Comment.objects.filter(post=self)[0]
        return comments.get_descendants()
        
    def getTags(self):
        """Return tags in post"""
        return PostWithTag.objects.filter(post=self)

    def insertTags(self, tags):
        """Insert new tags and assign it to post"""
        tags = tags.split(',')
        for tag in tags:
            if tag != '':
                try:
                    tag_object = Tag.objects.filter(name=tag)[0]
                except:
                    tag_object = Tag()
                    tag_object.name = tag
                    tag_object.save()
                post_in_tag = PostWithTag()
                post_in_tag.tag = tag_object
                post_in_tag.post = self
                post_in_tag.save()

    def removeTags(self):
        """Remove tags"""
        PostWithTag.objects.filter(post=self).delete()
        
    def setBlog(self, blog):
        """Set blog to post"""
        if int(blog) == 0:
	  self.blog = None
	else:
	  self.blog = Blog.objects.get(id=blog)
	  
    def createCommentRoot(self):
        """Create comment root for post"""
        comment_root = Comment.add_root(post=self, created=datetime.datetime.now())
        return comment_root
        
    def _getContent(self, type = 0):
        """Return post content, 0 - preview, 1 - post"""
        if self.type > 2:
	  return Answer.objects.filter(post=self)
	elif type == 0:
	  return self.preview
	else:
	  return self.text
	  
    def getContent(self, type = 0):
       """_getContent wrapper"""
       return self._getContent(type)
	  
    def getFullContent(self, type = 1):
       """Return preview"""
       return self._getContent(1)
	  
    def setText(self, text):
        """Set text and preview"""
        text = _parser.parse(text)
        [self.preview, self.text] = _parser.cut(text)
        
    def checkVote(self, user):
      """Check vote access"""
      if self.type > 2:     
	    vote = AnswerVote.objects.get(answer=self, user=user)
      if vote:
	    return 1
      else:
        return 0
	  
    def rate(self, user, value):
        """Rate post"""
        if not PostRate.objects.get(post=self, user=user):
	    self.rate += value
	    self.rate_count += 1
	    rate = PostRate()
	    rate.post = self
	    rate.user = user
	    rate.save()
	    return 1
	else:
	    return 0
	    

class PostWithTag(models.Model):
    """match posts with tags"""
    tag = models.ForeignKey(Tag)
    post = models.ForeignKey(Post)

    def __unicode__(self):
        """Return tag name"""
        return self.tag.name
    
class Comment(NS_Node):
    """Comments table"""
    post = models.ForeignKey(Post)
    #root = models.ForeignKey('self', null=True, blank=True, related_name='child_set')
    #root = models.IntegerField(null=True)
    author = models.ForeignKey(User, null=True, blank=True)
    text = models.TextField(blank=True)
    rate = models.IntegerField(null=True)
    rate_count = models.IntegerField(null=True)
    
    # Exception Value: Cannot use None as a query value
    created = models.DateTimeField(editable=False)
    
    
    node_order_by = ['created']
    
    
    #def getComment(self):
    #    """Return second levels comments"""
    #    return self.objects.filter(id=root)

    def __unicode__(self):
        """Return comment content"""
        return self.text
    
    @models.permalink
    def get_absolute_url(self):
        return ('node-view', ('ns', str(self.id),))
    
    def getMargin(self):
        return (self.depth - 2) * 20
    
    class Meta:
        ordering = ['id']
        
    def rate(self, user, value):
        """Rate Comment"""
        if not CommentRate.objects.get(comment=self, user=user):
	    self.rate += value
	    self.rate_count += 1
	    rate = ComentRate()
	    rate.comment = self
	    rate.user = user
	    rate.save()
	    return 1
	else:
	    return 0


class UserInBlog(models.Model):
    """Compared list of users and blogs"""
    user = models.ForeignKey(User)
    blog = models.ForeignKey(Blog)

    def __unicode__(self):
        return self.blog.name

    def getId(self):
        return self.blog.id

class BlogWithUser(UserInBlog):
    """Abstract class"""
    def __unicode__(self):
        return self.parent.user.username

    class Meta:
        abstract = True


class Profile(models.Model):
    """User profile"""
    user = models.ForeignKey(User, unique=True)
    city = models.ForeignKey(City, blank=True, null=True)
    icq = models.CharField(max_length=10, blank=True)
    jabber = models.CharField(max_length=60, blank=True)
    site = models.URLField(blank=True)
    rate = models.IntegerField(null=True)
    rate_count = models.IntegerField(null=True)
    posts_rate = models.IntegerField(null=True)
    comments_rate = models.IntegerField(null=True)
    blogs_rate = models.IntegerField(null=True)
    timezone = models.SmallIntegerField(null=True)
    avatar = models.CharField(max_length=60, blank=True)
    hide_mail = models.SmallIntegerField(null=True)
    reply_post = models.SmallIntegerField(null=True, default=1)
    reply_comment = models.SmallIntegerField(null=True, default=1)
    reply_pm = models.SmallIntegerField(null=True, default=1)
    about = models.TextField(blank=True)
    other = models.TextField(blank=True)
    
    def getPosts(self):
        """Get posts by user"""
        return Post.objects.filter(author=self.user)
        
    def getFriends(self):
        """Get user friends"""
        return Friends.objects.filter(user=self).user
        
    def getSendedMessages(self):
        """Get messages sended by user"""
        return Messages.objects.filter(sender=self.id)
        
    def getRecievedMessages(self):
        """Get messages recieved by user"""
        return Messages.objects.filter(recivier=self)

    def getBlogs(self):
        """Get blogs contain it"""
        return UserInBlog.objects.filter(user=self.user)
        
    def rate(self, user, value):
        """Rate user"""
        if not UserRate.objects.get(user=self):
			self.rate += value
			self.rate_count += 1
			rate = UserRate()
			rate.profile = self
			rate.user = user
			rate.save()
			return 1
        else:
			return 0    

    def __unicode__(self):
        """Return username"""
        return self.user.username;

class Friends(models.Model):
    """Friends table"""
    friend = models.IntegerField()
    user = models.ForeignKey(User)

class Messages(models.Model):
    """PM's"""
    sender = models.IntegerField()
    recivier = models.ForeignKey(User)
    text = models.TextField()
    deleted = models.IntegerField(null=True)
    
    def remove(self):
        """Remove message"""
        self.deleted += 1
        if self.deleted == 2:
            self.delete()
            
class Answer(models.Model):
    """Answers class"""
    post = models.ForeignKey(Post)
    vote = models.IntegerField(null=True)
    value = models.TextField()
    
    def fix(self, user):
        """Fixate votes and block next vote"""
        reply = AnswerVote()
        reply.answer = self.answer
        reply.user = user
        reply.save()
    
    def _vote(self, user, multiple):
        """Vote to answer"""
        if multiple == False:
	  self.fix(user)
        self.vote += 1
        self.save()
        
    def check(self, user):
        """Check vote access"""
        vote = AnswerVote.objects.filter(answer=self.post, user=user)
        if vote[0]:
	    return 0
	else:
	    return 1
	    
    def vote(self, user, multiple = False):
        """Vote to answer"""
        if self.check(user):
	    self._vote(user)
	    return 1
	else:
	    return 0
	    
class AnswerVote(models.Model):
    answer = models.ForeignKey(Post)
    user = models.ForeignKey(User)
    
class Favourite(models.Model):
    """Favourite posts table"""
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User)

class Spy(models.Model):
    """Spyed posts table"""
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User)

class PostRate(models.Model):
    """Post rates"""
    post = models.ForeignKey(Post)
    user = models.ForeignKey(User)
    
class CommentRate(models.Model):
    """Comment rates"""
    comment = models.ForeignKey(Comment)
    user = models.ForeignKey(User)
    
class BlogRate(models.Model):
    """Blog rates"""
    blog = models.ForeignKey(Blog)
    user = models.ForeignKey(User)
    
class UserRate(models.Model):
    """User rates"""
    profile = models.ForeignKey(Profile)#voted
    user = models.ForeignKey(User)#who vote
