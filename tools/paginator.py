from tools.shortcuts import to_json
from django.conf import settings
from functools import wraps


class Paginated(object):
    """Shit less, reusable and serializable paginator"""
    json_fields = (
        ('content', 'content_json'), 'page',
        'count', 'next_page_available',
        'prev_page_available', 'pages_count',
    )

    def __init__(self, qs, page=0, per_page=getattr(settings, 'PER_PAGE', 10)):
        self.qs = qs
        self.page = int(page)
        self.per_page = int(per_page)

    @property
    def content(self):
        if not hasattr(self, '_content'):
            self._content = self.qs[self.page * self.per_page:][:self.per_page]
        return self._content

    @property
    def count(self):
        if not hasattr(self, '_count'):
            self._count = self.qs.count()
        return self._count

    def next_page_available(self):
        return self.count > (self.page + 1) * self.per_page

    def next_page(self):
        return self.page + 1

    def prev_page_available(self):
        return self.page > 0

    def prev_page(self):
        return self.page - 1

    def pretty_number(self):
        return self.page + 1

    def pages_count(self):
        return self.count / self.per_page + 1

    def content_json(self):
        return map(to_json, self.content)

    def __iter__(self):
        for item in self.content:
            yield item


def paginated_json(fnc):
    """Return paginated json"""
    @wraps(fnc)
    def wrapper(request, page=0, *args, **kwargs):
        result = fnc(request, page, *args, **kwargs)
        return to_json(Paginated(result, page))
    return wrapper
