from django.conf.urls import patterns, include, url


urlpatterns = patterns('blogging.views',
    url(
        '^post/(?P<post_id>\d*)/$', 'post_page', 
        name='blogging_post_page',
    ),
    url(
        '^blog/(?P<blog_slug>.*)/$', 'blog_posts', 
        name='blogging_blog_posts',
    ),
    url(
        '^user/(?P<username>.*)/posts/$', 'user_posts', 
        name='blogging_user_posts',
    ),
    url(
        '^(?P<section_slug>.*)/$', 'section_posts', 
        name='blogging_section_posts',
    ),
    url(
        '^$', 'section_posts', 
        name='blogging_section_posts',
    ),
)
