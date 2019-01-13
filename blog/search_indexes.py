# -*- coding: utf-8 -*-
from haystack import indexes
from blog.models import Entry


class EntryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)
    content_auto = indexes.EdgeNgramField(model_attr="body")

    def get_model(self):
        return Entry

    def index_queryset(self, using=None):
        return self.get_model().published.select_related("author").all()
