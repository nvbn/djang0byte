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
from django import forms
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from pytils.translit import slugify, translify
from time import strftime
import urllib
import xml.dom.minidom
import simplejson
from django.utils.translation import ugettext as _


def jsend(data):
    """Alias for sending 'jsoned' data"""
    return(HttpResponse(simplejson.dumps(data), mimetype='application/json'))


def file_upload_path(instance, filename):
    """Generates upload path
    
    Keyword arguments:
    instance -- FileField
    filename - String
    
    Returns: String
    
    """
    parts = filename.rsplit('.', 1)
    name = "%s.%s" % (slugify(translify(parts[0])), slugify(translify(parts[1])))
    return "%s/%s/%s/%s" % (strftime('%Y'), 
       strftime('%m'), strftime('%d'), name)

def get_status(url):
    """Parse rss and get status

    Keyword arguments:
    url -- String

    Returns: String/Boolena

    """
    try:
        document = xml.dom.minidom.parse(urllib.urlopen(url))
        return(document.getElementsByTagName('item')[0].getElementsByTagName('description')[0].firstChild.data)
    except:
        return(False)

def new_notify_email(comment, type, recipient):
    default_protocol = getattr(settings, 'DEFAULT_HTTP_PROTOCOL', 'http')
    try:
        current_domain = Site.objects.get_current().domain
        templates = {
            'mention': "notify/mention.html",
            'post_mention': "notify/post_mention.html",
            'post_reply': "notify/post_reply.html",
            'spy_reply': "notify/spy_reply.html",
            'comment_reply': "notify/comment_reply.html",
        }
        subject = {
            'mention': _("User %(user)s mention your on %(site)s"),
            'post_mention': _("User %(user)s mention your on %(site)s"),
            'post_reply': _("User %(user)s write reply to your post on %(site)s"),
            'spy_reply': _("User %(user)s write reply to your spy post on %(site)s"),
            'comment_reply': _("User %(user)s write reply to your comment on %(site)s"),
        }
        message = render_to_string(templates[type], {
            'site_url': '%s://%s' % (default_protocol, current_domain),
            'comment': comment,
        })
        mail = send_mail(subject=subject[type] % {
                'user': comment.author.username,
                'site': current_domain
            }, message=message,
            recipient_list=[recipient.email]
        )
        mail.save()
    except Exception, e:
        print e
        pass #fail silently


class Access(object):
    new_post = 0
    new_blog = 1
    new_comment = 2
    rate_post = 3
    rate_comment = 4
    rate_user = 5
    rate_blog = 6


RATE_PLUS = '1'
RATE_MINUS = '0'
RATE = {
    RATE_PLUS: +1,
    RATE_MINUS: -1,
}


class ModelFormWithUser(forms.ModelForm):
    """Model form with user"""

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(ModelFormWithUser, self).__init__(*args, **kwargs)


class FormWithUser(forms.Form):
    """Form with user"""

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(FormWithUser, self).__init__(*args, **kwargs)
