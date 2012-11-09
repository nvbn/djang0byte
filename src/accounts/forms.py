from django.contrib.auth.models import User
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django import forms
import json


class ChangeUserForm(forms.ModelForm):
    """Change user form"""
    city = forms.CharField(required=False)
    services = forms.CharField(required=False)

    def clean_services(self):
        """Validate remote services"""
        if not self.cleaned_data.get('services'):
            return None
        services = json.loads(self.cleaned_data['services'])
        validate = URLValidator()
        for name, url in services.items():
            validate(url)
        return services

    def save(self, *args, **kwargs):
        """Save changed user"""
        if self.cleaned_data.get('city'):
            self.instance.set_city(self.cleaned_data['city'])
        if self.cleaned_data.get('services'):
            self.instance.services = self.cleaned_data['services']
        return super(ChangeUserForm, self).save(*args, **kwargs)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'avatar',
            'jabber', 'site', 'icq', 'about',
        )
    
    
