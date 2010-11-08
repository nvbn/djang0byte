from BeautifulSoup import BeautifulSoup, Comment


def parse(value, valid_tags = 'p i strong b u a h1 h2 h3 pre br img',
    valid_attrs = 'href src'):
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
        tag.attrs = [(attr, val) for attr, val in tag.attrs
                     if attr in valid_attrs]
    return soup.renderContents().decode('utf8')

def cut(text):
    """Cut text.
    
    Keyword arguments:
    text -- String
       
    Returns: String
        
    """
    cutted = text.split('[cut]')
    if cutted.length() == 2:
        return cutted[0], text
    cutted = text.split('[fcut]')
    if cutted.length() == 2:
        return cutted[0], cutted[1] + '[fcut]'
    else:
        return text, text
