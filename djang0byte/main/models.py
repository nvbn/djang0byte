# -*- coding: utf-8 -*-
from treebeard.ns_tree import NS_Node
from django.contrib.auth.models import User
from django.db import models


class Blog(models.Model):
    """Blog entrys"""
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(User)
    description = models.TextField()
    rate = models.IntegerField(null=True)
    rate_count = models.IntegerField(null=True)
    
    def getUsers(self):
        """Get user in this blog"""
        return UserInBlog.objects.filter(blog=self)
        
    def getPosts(self):
        """Get posts in blog"""
        return Post.objects.filter(blog=self)

class Tag(models.Model):
    """Tags table"""
    name = models.CharField(max_length=30)
    
    def getPosts(self):
        """Get posts with tag"""
        return PostWithTag.objects.filter(tag=self)

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
        (3, 'Answer')
    )

    author = models.ForeignKey(User)
    date = models.DateTimeField(auto_now=True)
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
        comments = Comment.objects.filter(post=self)
        out = []
        for comment in comments:
	    out.append(comment.dump_bulk())
        return out
        #return 0
        #return Comment.objects.filter(post=self, root=0)
        
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
    author = models.ForeignKey(User)
    text = models.TextField()
    rate = models.IntegerField(null=True)
    rate_count = models.IntegerField(null=True)
    
    node_order_by = ['id']
    
    
    #def getComment(self):
    #    """Return second levels comments"""
    #    return self.objects.filter(id=root)

    def __unicode__(self):
        """Return comment content"""
        return self.text
    
    class Meta:
        ordering = ['id']


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

