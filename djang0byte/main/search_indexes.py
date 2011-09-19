from haystack import indexes, site
from main.models import Post

class PostIndex(indexes.SearchIndex):
    """Full text post index"""
    title = indexes.CharField(model_attr='title')
    preview = indexes.CharField(model_attr='preview')
    text = indexes.CharField(model_attr='text', document=True)
    raw_tags = indexes.CharField(model_attr='raw_tags')
    id = indexes.IntegerField(model_attr='id')
    author = indexes.CharField(model_attr='author__username')

    def index_queryset(self):
        """Get qs for indexation"""
        return Post.objects.filter(
            is_draft=False,
        )

site.register(Post, PostIndex)