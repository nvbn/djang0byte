from django.contrib.auth.decorators import login_required
from annoying.decorators import render_to
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from simplepagination import paginate
from main.forms import CreatePostTranslateForm, CreatePostLinkForm, CreatePostForm
from main.models import *

@login_required
@render_to('drafts.html')
@paginate(style='digg', per_page=10)
def draft(request):
    drafts = Draft.objects.filter(author=request.user, is_draft=True).order_by('-id')
    return({'object_list': drafts})

@login_required
def edit_draft(request, id):
    draft = Draft.objects.get(id=id, author=request.user)
    if draft.type < 3:
        if draft.type == 0:
            form = CreatePostForm
        elif draft.type == 1:
            form = CreatePostLinkForm
        elif draft.type == 2:
            form = CreatePostTranslateForm
        if request.method == 'POST':
            form = form(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                draft.set_data(data)
                if request.POST.get('draft'):
                    post = draft
                else:
                    post = Post.from_draft(draft)
                post.save(edit=False)
                if not request.POST.get('draft'):
                  return HttpResponseRedirect('/post/%d/' % (post.id))
            else:
                draft.set_data(form.cleaned_data)
                return render_to_response('newpost.html',
                        {'form': form, 'blogs': Blog.create_list(request.user.get_profile()), 'type': draft.type, 'extend': 'base.html'},
                         context_instance=RequestContext(request))
        else:
            data = {'tags': draft.raw_tags, 'title': draft.title, 'text': draft.text, 'source':draft.adittion, 'link': draft.adittion}
            form = form(data)
            return render_to_response('newpost.html',
                        {'form': form, 'blogs': Blog.create_list(request.user.get_profile()),
                         'type': draft.type, 'extend': 'base.html', 'draft': True, 'id': draft.id},
                         context_instance=RequestContext(request))
    return HttpResponseRedirect('/draft/')
