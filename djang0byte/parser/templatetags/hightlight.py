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



from pygments import highlight
from pygments.lexers import get_lexer_by_name, PhpLexer
from pygments.formatters import HtmlFormatter
from pygments.util import ClassNotFound
from BeautifulSoup import BeautifulSoup

@register.filter
def highlight_template(value):
  soup = BeautifulSoup(value)
  for code in soup.findAll('code'):
    lang = code['lang']
    try:
      lexer = get_lexer_by_name(lang, encoding='utf-8', stripall=True, startinline=True)
    except ClassNotFound:
      lexer = get_lexer_by_name('text')
    formatter = HtmlFormatter(encoding='utf-8', style='colorful', linenos='table', cssclass='highlight', lineanchors="line")
    code = highlight(code, lexer, formatter)  
  return soup.renderContents().decode('utf8')

print highlight_template('''asdasdsad<code lang="bash">ls
rm -rf/''')
