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
