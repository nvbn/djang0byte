from tools.decorators import render_to
from blogging.models import Section, Post


@render_to
def section_page(request, section_slug=None):
    """Section with posts page"""
    try:
        section = Section.objects.get(slug=section_slug)
    except Section.DoesNotExist:
        section = Section.objects.get(is_default=True)
    return {
        'section': section,
    }
