# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
from main.models import Post
from django.db.models import Q

class Command(BaseCommand):

    def handle(self, **options):
        qs = Post.objects.filter(
            Q(title__icontains=u'решен') | Q(title__icontains=u'решён') | Q(title__icontains=u'solv'),
            blog__type__is_qa=True,
        )
        print 'fix %d posts' % qs.count()
        for post in qs: #Shit, update not work
            post.solved = True
            post.save(convert=True)
