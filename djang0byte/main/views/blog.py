from django.http import HttpResponse
from django.shortcuts import render_to_response
from main.forms import CreateBlogForm
from django.contrib import auth
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from main.models import *

@login_required
def newblog(request):
    if request.method == 'POST':
        form = CreateBlogForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            blog = Blog()
            blog.name = data['name']
            blog.description = data['description']
            blog.owner = request.user
            blog.save()
    else:
        form = CreateBlogForm()
    return render_to_response('newblog.html', {'form': form})
