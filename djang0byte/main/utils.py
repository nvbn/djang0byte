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
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.mail import send_mail
from django.http import HttpResponse
from django.template.loader import render_to_string
from pytils.translit import slugify, translify
from time import strftime
from sendmail.models import Mails
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
    str = "%s.%s" % (slugify(translify(parts[0])), slugify(translify(parts[1])))
    return "%s/%s/%s/%s" % (strftime('%Y'), 
       strftime('%m'), strftime('%d'), str)

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
            'mention': _("User %s mention your on %s") % (comment.author.username, current_domain),
            'post_mention': _("User %s mention your on %s") % (comment.author.username, current_domain),
            'post_reply': _("User %s write reply to your post on %s") % (comment.author.username, current_domain),
            'spy_reply': _("User %s write reply to your spy post on %s") % (comment.author.username, current_domain),
            'comment_reply': _("User %s write reply to your comment on %s") % (comment.author.username, current_domain),
        }
        message = render_to_string(templates[type], {
            'site_url': '%s://%s' % (default_protocol, current_domain),
            'comment': comment,
        })
        mail = Mails(subject=subject[type], message=message, recipient=recipient.email)
        mail.save()
    except Exception, e:
        print e
        pass #fail silently


class Access:
    new_post = 0
    new_blog = 1
    new_comment = 2
    rate_post = 3
    rate_comment = 4
    rate_user = 5
    rate_blog = 6