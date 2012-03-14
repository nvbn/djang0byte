from functools import partial
from django.contrib.auth.decorators import login_required
from annoying.decorators import render_to
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template.context import RequestContext
from django.views.decorators.cache import never_cache
from simplepagination import paginate
from main.forms import post_forms, EditDraftForm
from main.models import *
from djang0parser.utils import unparse

@never_cache
@login_required
@render_to('drafts.html')
@paginate(style='digg', per_page=10)
def draft(request):
    drafts = Draft.objects.filter(author=request.user, is_draft=True).order_by('-id')
    return {
        'object_list': drafts
    }


@never_cache
@login_required
def edit_draft(request, id=None):
    if id:
        form = partial(EditDraftForm, instance=get_object_or_404(
            Draft, id=id, author=request.user,
        ))
    else:
        form = EditDraftForm
    if request.method == 'POST':
        form = form(request.POST)
        if form.is_valid():
            draft = form.save()
            if not id:
                return redirect(reverse('main_edit_draft', args=(draft.id,)))
    else:
        form = form()
    return {
        'form': form,
    }


@login_required
def delete_draft(request, id):
    """Remove draft

    Keywords Arguments:
    id -- int -- draft id

    Returns: redirect
    """
    draft = get_object_or_404(
        Draft, id=id,
        author=request.user,
        is_draft=True
    )
    draft.delete()
    return HttpResponseRedirect('/draft/')