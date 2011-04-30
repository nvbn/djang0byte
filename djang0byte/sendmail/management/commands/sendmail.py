from django.core.management.base import BaseCommand, CommandError
from djang0byte.sendmail.models import Mails

class Command(BaseCommand):
    args = ''
    help = 'send mails'

    def handle(self, *args, **options):
        Mails.send_all()