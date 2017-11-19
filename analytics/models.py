# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


class PageView(models.Model):
    domain = models.URLField(null=False)
    url = models.FilePathField()
    title = models.TextField(null=False)
    ip = models.GenericIPAddressField(null=False)
    referrer = models.TextField(null=False)
    timestamp = models.DateTimeField(null=False)
    headers = models.TextField(null=False)
    session_id = models.CharField(null=False, max_length=255)

    class Meta:
        verbose_name = _("Page View")
        verbose_name_plural = _("Page Views")
        db_table = 'page_view'
        default_related_name = 'page_view'

    def __str__(self):
        return "{0}{1}".format(self.domain,
                               self.url)

    def get_browser(self):
        return ''

    def get_browser_icon(self):
        return ''
