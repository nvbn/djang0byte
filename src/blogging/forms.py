from django import forms
from blogging.models import Post, Comment, Blog
from tools.parser import parser
from accounts.middleware import get_current_user


class PostForm(forms.ModelForm):
    """Post editing/creating form"""
    def clean_content(self):
        """Clean content"""
        raw_content = self.cleaned_data.get('content')
        if not len(raw_content):
            raise forms.ValidationError('Content too short')
        preview, content = parser.cut(raw_content)
        self.instance.preview = parser.parse(preview)
        return parser.parse(content)

    def clean_related_url(self):
        """Clean related url"""
        url = self.cleaned_data.get('related_url')
        _type = self.cleaned_data.get('type')
        if not url and  _type in (
            Post.TYPE_LINK, Post.TYPE_TRANSLATE,
        ):
            raise forms.ValidationError('This type request related url')
        elif url and _type == Post.TYPE_POST:
            raise forms.ValidationError('This type not allow related url')
        return url

    def save(self, *args, **kwargs):
        """Set author if not exist"""
        try:
            if not self.instance.author:
                raise
        except Exception:
            self.instance.author = get_current_user()
        return super(PostForm, self).save(*args, **kwargs)

    class Meta:
        model = Post
        fields = (
            'title', 'content', 'blog',
            'tags', 'is_draft', 'type',
            'related_url',
        )
    

class PostOptionsForm(forms.ModelForm):
    """Post options form"""
    class Meta:
        model = Post
        fields = (
            'is_attached', 'is_commenting_locked',
            'is_rate_enabled',
        )


class CommentForm(forms.ModelForm):
    """Creating/updating comment form"""

    def clean_content(self):
        """Clean content"""
        content = self.cleaned_data.get('content')
        if not content:
            raise forms.ValidationError('Comment to short')
        return parser.parse(content)

    def save(self, *args, **kwargs):
        """Set author if not exist"""
        try:
            if not self.instance.author:
                raise
        except Exception:
            self.instance.author = get_current_user()
        return super(CommentForm, self).save(*args, **kwargs)

    class Meta:
        model = Comment
        fields = (
            'parent', 'content', 'post',
        )    
