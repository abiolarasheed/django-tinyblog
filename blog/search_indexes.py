# -*- coding: utf-8 -*-
from haystack import indexes
from blog.models import Entry


class EntryIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        return Entry

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(is_published=True)
