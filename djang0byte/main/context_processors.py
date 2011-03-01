from main.models import *
from main.utils import Access
from settings import POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT, MENU_CACHE_TIME, SIDEBAR_CACHE_TIME, LANGUAGE_CODE
import random, time
from django.contrib.auth.decorators import login_required

def djbyte(request):
    """Get special variables into template"""
    rate = None
    if request.user.is_authenticated():
        try:
            rate = Profile.objects.get(user=request.user).get_rate()
        except Profile.DoesNotExist:
            pass
    posts = Post.objects.order_by('-date').all()[0:][:20]
    comments = Comment.objects.select_related('post').order_by('-created').exclude(depth=1).all()[0:][:20]
    objects = [{'type': 'post', 'date': post.date, 'object': post} for post in posts]
    objects += [{'type': 'comment', 'date': comment.created, 'object': comment} for comment in comments]
    #bubble sort, yeba! =)
    def quicksort(L):
        todate = lambda date: time.mktime(date.timetuple())
        if len(L) > 1:
          pivot = random.randrange(len(L))
          elements = L[:pivot]+L[pivot+1:]
          left  = [element for element in elements if todate(element['date']) < todate(L[pivot]['date'])]
          right = [element for element in elements if todate(element['date']) >= todate(L[pivot]['date'])]
          return quicksort(left)+[L[pivot]]+quicksort(right)
        return L
    objects = quicksort(objects)
    objects.reverse()
    objects = objects[:20]
    try:
        profiles = Profile.objects.select_related('user').extra(select={'fullrate':
            'rate+%f*posts_rate+%f*blogs_rate+%f*comments_rate'
            % (POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT), },
            order_by=['-fullrate',])[0:][:10]
        profiles = [{'name': profile.user.username, 'rate': profile.get_rate()} for profile in profiles]
    except Profile.DoesNotExist:
        profiles = []
    blogs = Blog.objects.order_by('-rate')[0:][:10]
    return({'your_rate': rate, 'top_post_comment': objects, 'top_profiles': profiles, 'top_blogs': blogs,
            'blogs_count': Blog.objects.count(), 'profiles_count': Profile.objects.count(),
            'city_count': City.objects.count(), 'MENU_CACHE_TIME': MENU_CACHE_TIME, 'SIDEBAR_CACHE_TIME': SIDEBAR_CACHE_TIME,
            'LANGUAGE_CODE': LANGUAGE_CODE})

@login_required
def permission(request):
    profile = request.user.get_profile()
    return {
        'PERM_DELETE_POST': request.user.has_perm('main.delete_post'),
        'PERM_EDIT_POST': request.user.has_perm('main.change_post'),
        'PERM_CREATE_POST': profile.check_access(Access.new_post),
        'PERM_DELETE_COMMENT': request.user.has_perm('main.delete_comment'),
        'PERM_EDIT_COMMENT': request.user.has_perm('main.edit_comment'),
        'PERM_CREATE_COMMENT': profile.check_access(Access.new_comment),
        'PERM_DELETE_BLOG': request.user.has_perm('main.delete_blog'),
        'PERM_EDIT_BLOG': request.user.has_perm('main.change_blog'),
        'PERM_CREATE_BLOG': profile.check_access(Access.new_blog),
    }