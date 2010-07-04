# -*- coding: utf-8 -*-
from main.models import *

def install(request):
  comment_root = Comment.add_root(id=0,post_id=0)
  comment_root.save()