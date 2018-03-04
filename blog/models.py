# -*- coding: utf-8 -*-
import os
from django.db import models
from django.utils import timezone
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.utils.translation import ugettext_lazy as _

from taggit.managers import TaggableManager

from blog.managers import PublishedEntryQuerySet
from blog.utils import FileUploader, pygmentify_html


class Entry(models.Model):
    title = models.CharField(max_length=500, unique=True, db_index=True, null=False, blank=False)
    slug = models.SlugField(max_length=140, unique=True, db_index=True, null=False,
                            blank=False, editable=False)
    author = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    body = models.TextField(null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)
    published_date = models.DateTimeField(null=True, blank=True, editable=False)
    poster = models.ImageField(null=True, blank=True, upload_to=
                               FileUploader(os.path.join('entry', 'poster')))
    is_published = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=1)  # we will change this later and write a better one later
    tags = TaggableManager()
    objects = models.Manager()
    published = PublishedEntryQuerySet.as_manager()

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

    def get_similar_post(self):
        return self.__class__.published.\
            filter(tags__in=self.tags.all()).exclude(id=self.id).distinct()

    def get_absolute_url(self):
        return reverse('entry_detail', kwargs={'slug': self.slug})

    def as_json(self):
        return {"title": self.title,
                "url": self.get_absolute_url(),
                'id': self.pk,
                'update_url': reverse('entry_update', kwargs={'pk':self.pk})
                }

    def get_poster(self):
        try:
            return self.poster.url
        except (AttributeError, ValueError):
            return "http://via.placeholder.com/318x224"

    def count_comments(self):
        return 0

    def count_words_in_text(self, word_length=5):
        total_words = 0
        for current_text in self.body:
            total_words += len(current_text) / word_length
        return total_words

    def estimate_reading_time(self):
        words_per_min = 200  # Word per min
        total_words = self.count_words_in_text()
        return round(total_words / words_per_min)

    def headline(self):
        res = self.body[:80]

        try:
            res = pygmentify_html(res, noclasses=True)
        except Exception as e:
            res = res[:80]
        finally:
            return mark_safe(res)

    def save(self, *args, **kwargs):
        if self.is_published and self.published_date is None:
            self.published_date = timezone.now()

        if not self.slug:
            self.slug = self.__get_unique_slug()

        super(Entry, self).save(*args, **kwargs)


class Image(models.Model):
    caption = models.CharField(max_length=255, blank=False, null=False)
    photo = models.ImageField(blank=False, null=False, upload_to=
                              FileUploader(path=os.path.join('entry', 'images')))
    entry = models.ForeignKey(Entry, blank=False, null=False,
                              on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    modified_at = models.DateTimeField(auto_now=True, editable=False)

    def __str__(self):
        return self.caption

    def get_absolute_url(self):
        return reverse('image_detail', kwargs={'pk': self.pk})

    def as_json(self):
        return dict(caption=self.caption,
                    photo=self.photo.url,
                    entry=self.entry.slug)
