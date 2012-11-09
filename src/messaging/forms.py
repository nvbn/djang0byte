from django import forms
from messaging.models import Message
from tools.parser import parser
from django.contrib.auth.models import User
from accounts.middleware import get_current_user


class MessageForm(forms.ModelForm):
    """New message form"""
    receiver = forms.CharField(required=True)

    def clean_receiver(self):
        """Clean receiver"""
        try:
            receiver = self.cleaned_data.get('receiver', '')
            self.instance.receiver = User.objects.get(
                username=receiver,
            )
            return receiver
        except User.DoesNotExist:
            raise forms.ValidationError('Receiver does not exist')

    def clean_content(self):
        """Clean content"""
        raw_content = self.cleaned_data.get('content')
        if not len(raw_content):
            raise forms.ValidationError('Content too short')
        return parser.parse(raw_content)

    def save(self, *args, **kwargs):
        """Set sender if not exist"""
        try:
            if not self.instance.sender:
                raise
        except Exception:
            self.instance.sender = get_current_user()
        return super(MessageForm, self).save(*args, **kwargs)

    class Meta:
        model = Message
        fields = (
            'title', 'content',
        )
