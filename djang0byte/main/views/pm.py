# -*- coding: utf-8 -*-
from django.db import transaction
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.shortcuts import render_to_response
from main.models import *
from main.forms import CreatePmForm

@login_required
def newpm(request):
    """Create and send PM"""
    if request.method == 'POST':
        form = CreatePmForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            if data['to'] != request.user.username:
                pm = Messages()
                pm.sender = request.user.id
                pm.title = data['title']
                pm.recivier = User.objects.get(username=data['to'])
                pm.text = data['text']
                pm.save()
                return HttpResponseRedirect('/pm/%d/' % (pm.id))
    else:
        form = CreatePmForm()
    return render_to_response('newpm.html', {'form': form})

@login_required
def showpm(request, id):
    """Show single PM"""
    pm = Messages.objects.get(id=id)
    if pm.sender == request.user.id or pm.recivier == request.user:
        return render_to_response('pm.html', {'pm': pm})
    else:
        return HttpResponseRedirect('/')

@login_required
def pmlist(request, type = 'recived', frm = 0):
    """Show list of sended or recivied PMs"""
    if type == 'recivied':
        pms = Messages.objects.filter(recivier=request.user)[frm:][:10]
    elif type == 'sended':
        pms = Messages.objects.filter(sender=request.user.id)
    return render_to_response('pm_list.html', {'pms': pms})
