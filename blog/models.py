# -*- coding: utf-8 -*-
from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager


class Entry(models.Model):
    title = models.CharField(max_length=500, unique=True, db_index=True, null=False, blank=False)
    slug = models.SlugField(max_length=140, unique=True, db_index=True, null=False, blank=False)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    body = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    published_date = models.DateTimeField(null=True, blank=True, editable=False)
    poster = models.ImageField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    tags = TaggableManager()

    class Meta:
        verbose_name = _("Entry")
        verbose_name_plural = _("Entries")
        db_table = 'entries'
        default_related_name = 'entries'

    def __str__(self):
        return self.title

    def __get_unique_slug(self):
        slug = slugify(self.title)
        unique_slug = slug
        num = 1
        while self.__class__.objects.filter(slug=unique_slug).exists():
            unique_slug = '{}-{}'.format(slug, num)
            num += 1
        return unique_slug

    def save(self, *args, **kwargs):
        if self.is_published and self.id is None:
            self.published_date = timezone.now().date()

        if not self.slug:
            self.slug = self.__get_unique_slug()

        super(Entry, self).save(*args, **kwargs)

