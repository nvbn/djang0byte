from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from tools.decorators import render_to
from tools.paginator import Paginated
from blogging.models import Section, Post, Blog


@render_to
def section_posts(request, section_slug=None, page=0):
    """Section with posts page"""
    if section_slug:
        section = get_object_or_404(Section, slug=section_slug)
    else:
        section = get_object_or_404(Section, is_default=True)
    return {
        'section': section,
        'posts': Paginated(section.get_posts(), page)
    }


@render_to
def blog_posts(request, blog_slug, page=0):
    """Blog with posts page"""
    blog = get_object_or_404(Blog, slug=blog_slug)
    return {
        'blog': blog,
        'posts': Paginated(blog.get_posts(), page),
    }


@render_to
def user_posts(request, username, page=0):
    """User posts page"""
    user = get_object_or_404(User, username=username)
    return {
        'user': user,
        'posts': user.get_posts(),
    }


@render_to
def post_page(request, post_id):
    """Post page"""
    return {
        'post': get_object_or_404(Post, id=post_id),
    }
