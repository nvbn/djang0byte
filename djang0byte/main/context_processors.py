from main.models import *
from settings import POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT
from django.core.exceptions import FieldError

def djbyte(request):
    """Get special variables into template"""
    rate = None
    if request.user.is_authenticated():
        try:
            rate = Profile.objects.get(user=request.user).getRate()
        except Profile.DoesNotExist:
            pass
    posts = Post.objects.order_by('-date').all()[0:][:10]
    comments = Comment.objects.select_related('post').order_by('-created').exclude(depth=1).all()[0:][:10]
    objects = [{'type': 'post', 'date': post.date, 'object': post} for post in posts]
    objects += [{'type': 'comment', 'date': comment.created, 'object': comment} for comment in comments]
    #bubble sort, yeba! =)
    for n in range(0,len(objects)):
        temp = 0
        for i in range(1, len(objects)):
            temp = objects[i]
            if objects[i]['date'] < objects[i-1]['date']:
                objects[i] = objects[i-1]
                objects[i-1] = temp
    objects = objects[0:][:10]
    try:
        profiles = Profile.objects.select_related('user').extra(select={'fullrate':
            'rate+%f*posts_rate+%f*blogs_rate+%f*comments_rate DESC'
            % (POST_RATE_COEFFICIENT, BLOG_RATE_COEFFICIENT, COMMENT_RATE_COEFFICIENT) },
            order_by='-fullrate')[0:][:10]
        profiles = [{'name': profile.user.username, 'rate': profile.getRate()} for profile in profiles]
    except FieldError:
        profiles = []
    blogs = Blog.objects.order_by('-rate')[0:][:10]

    return({'your_rate': rate, 'top_post_comment': objects, 'top_profiles': profiles, 'top_blogs': blogs,
            'blogs_count': Blog.objects.count(), 'profiles_count': Profile.objects.count(),
            'city_count': City.objects.count()})
