from django.conf import settings
from django.core.mail import send_mail
from django.db import models


class Mails(models.Model):
    subject = models.CharField(max_length=1000)
    message = models.TextField()
    recipient = models.EmailField()

    def send(self):
        try:
            send_mail(self.subject, self.message, settings.DEFAULT_FROM_EMAIL, self.recipient)
        except:
            pass

    @staticmethod
    def send_all():
        for mail in Mails.objects.all():
            print mail.subject
            mail.send()
            mail.delete()
