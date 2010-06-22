from django import forms

class RegisterForm(forms.Form):
    name = forms.CharField()
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class CreateBlogForm(forms.Form):
    name = forms.CharField()
    description = forms.CharField(widget=forms.Textarea)
