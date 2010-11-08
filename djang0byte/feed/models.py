from django.contrib.syndication.views import Feed
from main.models import Post

class PostFeed(Feed):
    title = "feed"
    link = "/rss/"
    description = ""

    def items(self):
        return Post.objects.order_by('-id')[:50]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.text
        
