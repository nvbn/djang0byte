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
from timezones.forms import TimeZoneField
from tagging_autocomplete.widgets import TagAutocomplete

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

class CreateBlogForm(forms.Form):
    """Create new blog form"""
    name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)

class CreatePostForm(forms.Form):
    """Create new post form"""
    title = forms.CharField()
    blog = forms.CharField()
    text = forms.CharField(widget=forms.Textarea())
    tags = forms.CharField(widget=TagAutocomplete(), required=False)

class CreatePostLinkForm(CreatePostForm):
    """Create post link form"""
    addition = forms.URLField()

class CreatePostTranslateForm(CreatePostForm):
    """Create post link form"""
    addition = forms.URLField()

class CreateCommentForm(forms.Form):
    """Create new comment form"""
    text = forms.CharField(widget=forms.Textarea)
    post = forms.IntegerField(widget=forms.HiddenInput)
    comment = forms.IntegerField(widget=forms.HiddenInput, required=False)
    
class EditUserForm(forms.Form):
    """Edit user settings form"""
    mail = forms.EmailField()
    show_mail = forms.BooleanField(required=False)
    icq = forms.CharField(required=False)
    jabber = forms.CharField(required=False)
    city = forms.CharField(required=False)
    timezone = TimeZoneField(required=False)
    site = forms.URLField(required=False)
    about = forms.CharField(widget=forms.Textarea, required=False)
    notify_post_reply = forms.BooleanField(required=False)
    notify_comment_reply = forms.BooleanField(required=False)
    notify_pm = forms.BooleanField(required=False)


class EditUserPick(forms.Form):
    userpic = forms.ImageField()

class EditPostForm(CreatePostForm):
    pass