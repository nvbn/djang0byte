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
import code
import re
from BeautifulSoup import BeautifulSoup
from pygments import highlight
from pygments.lexers import get_lexer_by_name, PhpLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound

from parser.models import Code

def parse(value, valid_tags = 'p i strong b u a h3 pre br img cut fcut  table tr td div pre span spoiler',
    valid_attrs = 'href src lang class name id style'):
    """Cleans non-allowed HTML from the input.
    
    Keyword arguments:
    value -- String
    valid_tags -- String
    valid_attrs -- String
       
    Returns: String
        
    """
    valid_tags = valid_tags.split()
    valid_attrs = valid_attrs.split()
    value = value.replace('\n', '<br />')
    soup = BeautifulSoup(value)
    for tag in soup.findAll(True):
        if tag.name not in valid_tags:
            tag.hidden = True
        for attr, val in tag.attrs:
            if re.match('javascript:', val, re.I) is not None:
                tag.hidden = True
            if tag.name == 'code' and attr == 'lang':
                try:
                    lexer = get_lexer_by_name(val, encoding='utf-8', stripall=True, startinline=True)
                except ClassNotFound:
                    lexer = get_lexer_by_name('text')
                formatter = HtmlFormatter(encoding='utf-8', style='colorful', linenos='table', cssclass='highlight', lineanchors="line")
                code = tag.__unicode__().replace('<br />', '')
                code_model = Code()
                code_model.code = code
                code_model.lang = val
                code_model.save()
                code = highlight(code, lexer, formatter)
                code = code.replace('<table class="highlighttable">', '<table class="highlighttable" id="%d">' % (code_model.id,))
                tag.replaceWith(code)
        tag.attrs = [(attr, val) for attr, val in tag.attrs if attr in valid_attrs]
    return soup.renderContents().decode('utf8')


def unparse(value):
    value = value.replace('<br />','\n')
    soup = BeautifulSoup(value)

    for code in soup.findAll({'table': True, 'class=highlighttable': True}):
        new_code = Code.objects.get(id=int(code['id']))
        code.replaceWith('<code lang="%s">%s</code>' % (new_code.lang, new_code.code))
    return soup.renderContents().decode('utf8')

def cut(text):
    """Cut text.
    
    Keyword arguments:
    text -- String
       
    Returns: String
        
    """
    cutted = text.split('<cut>')
    if len(cutted) == 2:
        return cutted[0], text
    cutted = text.split('<fcut>')
    if len(cutted) == 2:
        return cutted[0], '<fcut>' + cutted[1]
    else:
        return text, text