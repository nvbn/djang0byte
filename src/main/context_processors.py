from django.contrib.sites.models import Site
from django.shortcuts import redirect
from main.models import *
from main.utils import Access
from settings import POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT, MENU_CACHE_TIME, SIDEBAR_CACHE_TIME, LANGUAGE_CODE, SITENAME, TIME_ZONE, KEYWORD_MIN_COUNT, API_KEY, FEED_URL
import random, time
from django.contrib.auth.decorators import login_required
from itertools import imap, islice

def get_objects():
    posts = Post.objects.order_by('-date').select_related('author').all()[0:][:20]
    comments = Comment.objects.select_related('post', 'author').order_by('-created').exclude(depth=1).all()[0:][:20]
    objects = [
        {
            'type': 'post',
            'date': post.date,
            'object': post
        }   for post in posts
    ]
    objects += [
        {
            'type': 'comment',
            'date': comment.created,
            'object': comment
        } for comment in comments
    ]
    objects.sort(key = lambda element: element['date'], reverse = True)
    return objects

def djbyte(request):
    """Get special variables into template"""
    rate = None
    timezone = TIME_ZONE
    lenta_events_count = 0
    if request.user.is_authenticated():
        try:
            profile = Profile.objects.get(user=request.user)
            profile.update_last_visit()
            rate = profile.get_rate()
            timezone = profile.timezone
        except Profile.DoesNotExist:
            pass
        try:
            lenta_events_count = LentaLastView.objects.get(user=request.user).get_unseen_count()
        except LentaLastView.DoesNotExist:
            pass

    try:
        profiles = imap(lambda profile: {
                'name': profile.user.username,
                'rate': profile.get_rate()
            },
            Profile.objects.select_related('user').extra(select={
                'fullrate': 'rate+%f*posts_rate+%f*blogs_rate+%f*comments_rate'
                    % (POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT),
            },
            order_by=['-fullrate',])[0:][:10]
        )
    except Profile.DoesNotExist:
        profiles = []
    blogs = Blog.objects.order_by('-rate')[0:][:10]
    try:
        type = request.session['right_panel']
        right_panel_js = "fast_funcs['%s']()" % (type)
    except KeyError:
        right_panel_js = None
    online = LastVisit.get_online()
    last_users = User.objects.order_by('-id')[:10]
    return({
        'your_rate': rate,
        'top_post_comment': islice(get_objects(), 20),
        'top_profiles': profiles,
        'top_blogs': blogs,
        'blogs_count': Blog.objects.count(),
        'profiles_count': Profile.objects.count(),
        'TIMEZONE': timezone,
        'city_count': City.objects.count(),
        'MENU_CACHE_TIME': MENU_CACHE_TIME,
        'SIDEBAR_CACHE_TIME': SIDEBAR_CACHE_TIME,
        'LANGUAGE_CODE': LANGUAGE_CODE,
        'SITENAME': SITENAME,
        'RIGHT_PANEL_JS': right_panel_js,
        'API_KEY': API_KEY,
        'keywords': lambda: ', '.join(x.__unicode__() for x in Tag.objects.cloud_for_model(
            Post, min_count=KEYWORD_MIN_COUNT
        )[:10]),
        'FEED_URL': FEED_URL,
        'ONLINE': online,
        'LAST_USERS': last_users,
        'SITE_DOMAIN': Site.objects.get_current().domain,
        'lenta_events_count' : lenta_events_count,
    })

@login_required
def permission(request):
    profile = request.user.get_profile()
    return {
        'PERM_DELETE_POST': request.user.has_perm('main.delete_post'),
        'PERM_EDIT_POST': request.user.has_perm('main.change_post'),
        'PERM_CREATE_POST': profile.check_access(Access.new_post),
        'PERM_DELETE_COMMENT': request.user.has_perm('main.delete_comment'),
        'PERM_EDIT_COMMENT': request.user.has_perm('main.change_comment'),
        'PERM_CREATE_COMMENT': profile.check_access(Access.new_comment),
        'PERM_DELETE_BLOG': request.user.has_perm('main.delete_blog'),
        'PERM_EDIT_BLOG': request.user.has_perm('main.change_blog'),
        'PERM_CREATE_BLOG': profile.check_access(Access.new_blog),
    }