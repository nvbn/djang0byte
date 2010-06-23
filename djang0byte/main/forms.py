from django import forms

class RegisterForm(forms.Form):
    """Registration form"""
    name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class LoginForm(forms.Form):
    """Login form"""
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class CreateBlogForm(forms.Form):
    """Create new blog form"""
    name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)

class CreatePostForm(forms.Form):
    """Create new post form"""
    title = forms.CharField()
    text = forms.CharField(widget=forms.Textarea)
    tags = forms.CharField()
