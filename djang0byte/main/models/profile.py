from django.db import models
from django.contrib.auth.models import User
from post import Post

class Profile(models.Model):
    """User profile"""
    user = models.ForeignKey(User, unique=True)
    city = models.CharField(max_length=60)
    icq = models.CharField(max_length=10)
    jabber = models.CharField(max_length=60)
    site = models.URLField()
    rate = models.IntegerField()
    rate_count = models.IntegerField()
    posts_rate = models.IntegerField()
    comments_rate = models.IntegerField()
    blogs_rate = models.IntegerField()
    timezone = models.SmallIntegerField()
    avatar = models.CharField(max_length=60)
    hide_mail = models.SmallIntegerField()
    reply_post = models.SmallIntegerField()
    reply_comment = models.SmallIntegerField()
    reply_pm = models.SmallIntegerField()
    about = models.TextField()
    other = models.TextField()
    
    def getPosts(self):
        """Get posts by user"""
        return Post.objects.filter(author = self.user)
        
    def getFriends(self):
        """Get user friends"""
        return Friends.objects.filter(user = self)
        
    def getSendedMessages(self):
        """Get messages sended by user"""
        return Messages.objects.filter(sender = self.id)
        
    def getRecievedMessages(self):
        """Get messages recieved by user"""
        return Messages.objects.filter(recivier = self)

class Friends(models.Model):
    """Friends table"""
    friend = models.IntegerField()
    user = models.ForeignKey(User)

class Messages(models.Model):
    """PM's"""
    sender = models.IntegerField()
    recivier = models.ForeignKey(User)
    text = models.TextField()
    deleted = models.IntegerField()
    
    def remove(self):
        """Remove message"""
        self.deleted += 1
        if self.deleted == 2:
            self.delete()
