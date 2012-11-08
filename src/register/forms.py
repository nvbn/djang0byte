from captcha.forms import RegistrationFormCaptcha
from main.models import Profile


class RegistrationFormProfile(RegistrationFormCaptcha):
    """Wrapper form for profile creating"""

    def save(self, profile_callback=None):
        user = super(RegistrationFormProfile, self).save(profile_callback)
        profile = Profile(user=user)
        profile.save()
        return user