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
from django import forms
from django_push.publisher import ping_hub
from tagging.models import Tag
from timezones.forms import TimeZoneField
from tagging_autocomplete.widgets import TagAutocomplete
from main.models import Comment, Post, Blog, UserInBlog, Notify, Draft
from django.conf import settings
from djang0parser import utils
from main.utils import ModelFormWithUser, PRETTY_TIMEZONE_CHOICES
from django.utils.translation import ugettext as _


class RegisterForm(forms.Form):
    """Registration form"""
    name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class LoginForm(forms.Form):
    """Login form"""
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    save = forms.CheckboxInput()

class CreateBlogForm(ModelFormWithUser):
    """Create new blog form"""

    def save(self, commit=True):
        self.instance.owner = self.user
        inst = super(CreateBlogForm, self).save(commit)
        UserInBlog.objects.create(
            blog=inst,
            user=self.user,
        )
        return inst

    class Meta:
        model = Blog
        fields = ('description', 'name')


class CreatePostForm(ModelFormWithUser):
    """Create new post form"""

    def clean_blog(self):
        blog = self.cleaned_data.get('blog', None)
        if not blog.check_user(self.user):
            raise forms.ValidationError(_('You not in this blog!'))
        return blog

    def clean_addition(self):
        addition = self.cleaned_data.get('addition', None)
        if self.cleaned_data.get('type') in (Post.TYPE_LINK, Post.TYPE_TRANSLATE) and not addition:
            raise forms.ValidationError(_('This post type require addition!'))
        return addition

    def save(self, commit=True):
        inst = self.instance
        inst.author = self.user
        inst.preview, inst.text = utils.cut(inst.text)
        inst.preview = utils.parse(inst.preview, settings.VALID_TAGS, settings.VALID_ATTRS)
        inst.text = utils.parse(inst.text, settings.VALID_TAGS, settings.VALID_ATTRS)
        inst = super(CreatePostForm, self).save(commit)
        Tag.objects.update_tags(inst, inst.raw_tags)
        inst.create_comment_root()
        for mention in utils.find_mentions(inst.text):
            Notify.new_mention_notify(mention, post=inst)
        if settings.PUBSUB:
            ping_hub(settings.FEED_URL, hub_url=settings.PUSH_HUB)
        return inst

    class Meta:
        model = Post
        fields = (
            'type', 'blog', 'addition',
            'title', 'text', 'raw_tags',
        )


class EditDraftForm(ModelFormWithUser):
    """Edit or create draft form"""

    def clean_title(self):
        return self.cleaned_data.get('title', _('Unnamed post'))

    def save(self, commit=True):
        self.instance.author = self.user
        return super(EditDraftForm, self).save(commit)

    class Meta:
        model = Draft
        fields = fields = (
            'type', 'blog', 'addition',
            'title', 'text', 'raw_tags',
        )


class CreateCommentForm(forms.Form):
    """Create new comment form"""
    text = forms.CharField(widget=forms.Textarea)
    post = forms.IntegerField(widget=forms.HiddenInput)
    comment = forms.IntegerField(widget=forms.HiddenInput, required=False)

    def clean(self):
        """Clean and receive data"""
        data = self.cleaned_data
        try:
            data['post_obj'] = Post.objects.get(
                id=data['post'],
                disable_reply=False,
            )
        except Post.DoesNotExist:
            raise forms.ValidationError("Post not found")
        try:
            data['root'] = Comment.objects.select_related('author').get(
                id=data['comment'],
                post=data['post_obj'],
            )
        except Comment.DoesNotExist:
            data['root'] = Comment.objects.select_related('author').get(
                post=data['post_obj'],
                depth=1.
            )
        data['raw_text'] = data['text']
        data['text'] = utils.parse(data['text'], settings.VALID_TAGS, settings.VALID_ATTRS)
        return data
    
class EditUserForm(forms.Form):
    """Edit user settings form"""
    mail = forms.EmailField()
    show_mail = forms.BooleanField(required=False)
    icq = forms.CharField(required=False)
    jabber = forms.CharField(required=False)
    city = forms.CharField(required=False)
    timezone = TimeZoneField(required=False, choices=PRETTY_TIMEZONE_CHOICES)
    site = forms.URLField(required=False)
    about = forms.CharField(widget=forms.Textarea, required=False)
    notify_post_reply = forms.BooleanField(required=False)
    notify_comment_reply = forms.BooleanField(required=False)
    notify_pm = forms.BooleanField(required=False)
    notify_mention = forms.BooleanField(required=False)
    notify_spy = forms.BooleanField(required=False)

class PostOptions(forms.Form):
    """Edit post settings"""
    pinch = forms.BooleanField(required=False)
    disable_reply = forms.BooleanField(required=False)
    disable_rate = forms.BooleanField(required=False)

class EditUserPick(forms.Form):
    userpic = forms.ImageField()

class EditPostForm(CreatePostForm):
    pass

class SearchForm(forms.Form):
    """Search form"""
    query = forms.CharField()
