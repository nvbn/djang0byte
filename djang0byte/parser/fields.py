from django import newforms as forms
from BeautifulSoup import BeautifulSoup, Comment

class ParsedField(forms.CharField):

    widget=forms.widgets.Textarea(attrs={'dojoType': 'Editor2'})

    valid_tags = 'p i strong b u a h1 h2 h3 pre br img'
    valid_attrs = 'href src'

    def clean(self, value):
        """
        Cleans non-allowed HTML from the input.
        """
        self.valid_tags = self.valid_tags.split()
        self.valid_attrs = self.valid_attrs.split()
        value = super(Editor2Field, self).clean(value)
        soup = BeautifulSoup(value)
        for comment in soup.findAll(
            text=lambda text: isinstance(text, Comment)):
            comment.extract()
        for tag in soup.findAll(True):
            if tag.name not in self.valid_tags:
                tag.hidden = True
            tag.attrs = [(attr, val) for attr, val in tag.attrs
                         if attr in self.valid_attrs]
        return soup.renderContents().decode('utf8')
