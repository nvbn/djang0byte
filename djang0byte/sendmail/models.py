from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models


class Mails(models.Model):
    """Mail class"""
    subject = models.CharField(max_length=1000)
    message = models.TextField()
    recipient = models.EmailField()

    def send(self):
        """Send message"""
        try:
            #send_mail(self.subject, self.message, settings.DEFAULT_FROM_EMAIL, [self.recipient,])
            msg = EmailMessage(self.subject, self.message, settings.DEFAULT_FROM_EMAIL, [self.recipient,])
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
        except:
            pass

    @staticmethod
    def send_all():
        """Send all messages and delete sended"""
        for mail in Mails.objects.all():
            mail.send()
            mail.delete()
