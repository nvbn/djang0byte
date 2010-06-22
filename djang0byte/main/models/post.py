from django.db import models
from django.contrib.auth.models import User

class Blog(models.Model):
    """Blog entrys"""
    name = models.CharField(max_length=30)
    owner = models.ForeignKey(User)
    description = models.TextField()
    rate = models.IntegerField()
    rate_count = models.IntegerField()
    
    def getUsers(self):
        """Get user in this blog"""
        return UserInBlog.objects.filter(blog = self)
        
    def getPosts(self):
        """Get posts in blog"""
        return Post.objects.filter(blog = self)

class Tag(models.Model):
    """Tags table"""
    name = models.CharField(max_length=30)
    
    def getPosts(self):
        """Get posts with tag"""
        return PostWithTag.objects.filter(tag = self)
    
class Post(models.Model):
    """Posts table"""
    author = models.ForeignKey(User)
    blog = models.ForeignKey(Blog)
    title = models.CharField(max_length=300)
    preview = models.TextField()
    text = models.TextField()
    rate = models.IntegerField()
    rate_count = models.IntegerField()
    type = models.IntegerField()
    adittion = models.CharField(max_length=300)
    
    def getComment(self):
        """Return first level comments in post"""
        return Comment.objects.filter(post = self, root = 0)
        
    def getTags(self):
        """Return tags in post"""
        return PostWithTag.objects.filter(post = self)

class PostWithTag(models.Model):
    """match posts with tags"""
    tag = models.ForeignKey(Tag)
    post = models.ForeignKey(Post)
    
class Comment(models.Model):
    """Comments table"""
    post = models.ForeignKey(Post)
    root = models.IntegerField()
    author = models.ForeignKey(User)
    text = models.TextField()
    rate = models.IntegerField()
    rate_count = models.IntegerField()
    
    def getComment(self):
        """Return second levels comments"""
        return self.objects.filter(id = root)



class UserInBlog(models.Model):
    """Compared list of users and blogs"""
    user = models.ForeignKey(User)
    blog = models.ForeignKey(Blog)

