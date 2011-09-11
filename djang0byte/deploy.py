#djang0byte deploy script

import os
import sys
sys.path.append(os.getcwd())

if __name__ == '__main__':
    deps = open('deps', 'r')
    for dep in deps.readlines():
        if os.system('pip install %s' % (dep,)) != 0:
            sys.exit("Unable to install dependency: %s "
                "consider logging in as a superuser." % dep)

    os.environ["DJANGO_SETTINGS_MODULE"] = "settings"

    import settings
    from main.models import Profile
    from django.contrib.auth.models import User
    from treemenus.models import Menu

    if os.system('python manage.py syncdb') != 0:
        sys.exit("Unable to execute syncdb")

    Profile.objects.create(
        user=User.objects.get()
    )
    Menu.objects.create(
        name='menu'
    )
    Menu.objects.create(
        name='bottom_menu'
    )
