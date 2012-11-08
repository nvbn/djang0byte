# -*- coding:utf-8 -*-
from django.contrib.admin import site

from loginza import models

site.register(
    models.Identity,
    list_display=['id', 'provider', 'identity']
)
site.register(
    models.UserMap,
    list_display=['id', 'identity', 'user']
)