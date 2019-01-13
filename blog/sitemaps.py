# -*- coding: utf-8 -*-
from django.contrib import sitemaps
from django.urls import reverse

from blog.models import Entry


class StaticViewSitemap(sitemaps.Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return ["about", "feedback", "index", "entry_list"]

    def location(self, item):
        return reverse(item)


class BlogSitemap(sitemaps.Sitemap):
    changefreq = "never"
    priority = 0.9

    def items(self):
        return Entry.published.all().order_by("-modified_at")

    def lastmod(self, obj):
        return obj.modified_at
