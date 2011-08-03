#djang0byte deploy script

import os
import sys
sys.path.append(os.getcwd())
import settings
from main.models import Profile
from django.contrib.auth.models import User
from treemenus.models import Menu

if __name__ == '__main__':
    deps = open('deps', 'r')
    for dep in deps.readlines():
        os.system('pip install %s' % (dep,))
    os.system('python manage.py syncdb')
    Profile.objects.create(
        user=User.objects.get()
    )
    Menu.objects.create(
        name='menu'
    )
    Menu.objects.create(
        name='bottom_menu'
    )