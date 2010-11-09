# -*- coding: utf-8 -*-
#       This program is free software; you can redistribute it and/or modify
#       it under the terms of the GNU General Public License as published by
#       the Free Software Foundation; either version 2 of the License, or
#       (at your option) any later version.
#       
#       This program is distributed in the hope that it will be useful,
#       but WITHOUT ANY WARRANTY; without even the implied warranty of
#       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#       GNU General Public License for more details.
#       
#       You should have received a copy of the GNU General Public License
#       along with this program; if not, write to the Free Software
#       Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#       MA 02110-1301, USA.



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
