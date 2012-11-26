from django.conf.urls import patterns, include, url


urlpatterns = patterns('blogging.views',
    url(
        '^(?P<section_slug>.*)/$', 'section_posts', 
        name='blogging_section_posts',
    ),
    url(
        '^(?P<blog_slug>.*)/$', 'blog_posts', 
        name='blogging_blog_posts',
    ),
    url(
        '^(?P<username>.*)/$', 'user_posts', 
        name='blogging_user_posts',
    ),
)
