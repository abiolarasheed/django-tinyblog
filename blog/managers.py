# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import types
from django.db import models


class PublishedEntryQuerySet(models.QuerySet):
    """QuerySet that returns only published Entries."""

    @classmethod
    def as_manager(cls):
        def get_queryset(self):
            return (
                PublishedEntryQuerySet(self.model, using=self._db)
                .select_related("author")
                .filter(is_published=True)
            )

        #  Get the manger form the QuerySet class as_manager()
        manager = super(PublishedEntryQuerySet, cls).as_manager()

        # Replace the manager's get_queryset method with the one we have above
        manager.get_queryset = types.MethodType(get_queryset, manager)
        return manager
