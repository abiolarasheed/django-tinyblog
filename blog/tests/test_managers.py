# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.query import QuerySet
from django.test import TestCase
from ..models import Entry


class PublishedEntryQuerySetTestCase(TestCase):
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
