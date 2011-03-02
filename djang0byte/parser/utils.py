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
import re

from BeautifulSoup import BeautifulSoup

def parse(value, valid_tags = 'p i strong b u a h1 h2 h3 pre br img code',
    valid_attrs = 'href src lang'):
    """Cleans non-allowed HTML from the input.
    
    Keyword arguments:
    value -- String
    valid_tags -- String
    valid_attrs -- String
       
    Returns: String
        
    """
    value = value.replace('\n','<br />\n')
    valid_tags = valid_tags.split()
    valid_attrs = valid_attrs.split()
    soup = BeautifulSoup(value)
    for tag in soup.findAll(True):
        if tag.name not in valid_tags:
            tag.hidden = True
        for attr, val in tag.attrs:
            if re.match('javascript:', val, re.I) is not None:
                tag.hidden = True
        tag.attrs = [(attr, val) for attr, val in tag.attrs if attr in valid_attrs]
    return soup.renderContents().decode('utf8')

def cut(text):
    """Cut text.
    
    Keyword arguments:
    text -- String
       
    Returns: String
        
    """
    cutted = text.split('[cut]')
    if len(cutted) == 2:
        return cutted[0], text
    cutted = text.split('[fcut]')
    if len(cutted) == 2:
        return cutted[0], '[fcut]' + cutted[1]
    else:
        return text, text