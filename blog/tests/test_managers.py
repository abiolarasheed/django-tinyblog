# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.query import QuerySet
from django.test import TestCase
from ..models import Entry


class PublishedEntryQuerySetTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection
        get_redis_connection("default").flushall()

    def setUp(self):
        blog_title = "Test blog Title"
        blog_body = "This is my test blog"

        author, _ = get_user_model().\
            objects.get_or_create(email="iamatest@gmail.com", username="iamatest")

        [Entry.objects.get_or_create(title=blog_title + str(index),
                                     body=blog_body + str(index),
                                     author=author, is_published=True)
         for index in range(30)]
        Entry.objects.filter(id__gte=16).update(is_published=False)

    def test_entry_published(self):
        # Check if 'Entry' has attribute 'published'
        self.assertIsInstance(Entry.published, models.Manager)

        # Check if QuerySet was returned
        self.assertIsInstance(Entry.published.all(), QuerySet)

        # Check to see if 15 exist since we created 15 as published.
        self.assertEqual(Entry.published.all().order_by('id').count(), 15)

        # Check if all results 'is_published' value is the same
        self.assertEqual(Entry.published.all().
                         values('is_published').distinct().count(), 1)

        # Check if all results 'is_published' value is the same and is True
        self.assertTrue(Entry.published.all().
                        values('is_published').distinct()[0]['is_published'])
