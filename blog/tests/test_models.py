# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.test import TestCase
from ..models import Entry


class BlogModelTestCase(TestCase):
    def setUp(self):
        self.author, auth_created = User.objects.get_or_create(email="iamatest@gmail.com",
                                                               username="iamatest")
        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"

    def get_entry(self):
        return Entry.objects.get_or_create(title=self.blog_title,
                                           body=self.blog_body,
                                           author=self.author)

    def test_create(self):
        entry, created = self.get_entry()
        self.assertTrue(created)
        self.assertIsInstance(entry, Entry)
        self.assertEqual(entry.modified_at.date(), entry.created_at.date())
        self.assertIsNone(entry.published_date)
        self.assertFalse(entry.is_published)

    def test_on_publish(self):
        entry, created = self.get_entry()
        entry.is_published = True
        entry.save()
        self.assertNotEqual(entry.modified_at, entry.created_at)
        self.assertTrue(entry.is_published)
        self.assertIsNotNone(entry.published_date)

    def test_get_unique_slug(self):
        entry = Entry(title=self.blog_title,
                      body=self.blog_body,
                      author=self.author)

        slug = entry._Entry__get_unique_slug()
        self.assertFalse(" " in slug)
        self.assertTrue("-" in slug)

