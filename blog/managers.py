# -*- coding: utf-8 -*-
from django.db import models


class PublishedEntryQuerySet(models.QuerySet):
    """QuerySet that returns only published Entries."""
    pass
