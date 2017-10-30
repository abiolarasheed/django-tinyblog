# -*- coding: utf-8 -*-
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from django.test import TestCase
from django.urls.base import reverse
from django.utils.safestring import SafeText

from ..models import Entry


class BlogViewTestCase(TestCase):
    def generic_template_view_tester(self, path, path_name, template_name):
        # set variables.
        path = path
        path_name = path_name
        template_name = template_name

        # Check.
        self.assertEqual(path, reverse(path_name))
        self.assertEqual(get_template(template_name).template.name, template_name)
        self.assertIsInstance(get_template(template_name).render(), SafeText)

    def test_index_page(self):
        self.generic_template_view_tester('/', 'index', 'index.html')

    def test_about(self):
        self.generic_template_view_tester("/about/", 'about', "about.html")

    def test_feedback_blog(self):
        self.generic_template_view_tester('/blog/', 'blog', 'blog.html')

    def test_feedback(self):
        self.generic_template_view_tester("/feedback/", "feedback", "feedback.html")


class EntryViewTestCase(TestCase):
    def setUp(self):
        self.author, auth_created = get_user_model().\
            objects.get_or_create(email="iamatest@gmail.com", username="iamatest")
        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"
        self.entry = Entry.objects.get_or_create(title=self.blog_title,
                                                 body=self.blog_body,
                                                 author=self.author)[0]

    def test_basic_view(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertEqual(response.status_code, 200)

    def test_title_in_entry(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertContains(response, self.entry.title)

    def test_body_in_entry(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertContains(response, self.entry.body)


class EntryListViewTestCase(TestCase):
    def setUp(self):
        self.author, auth_created = get_user_model().\
            objects.get_or_create(email="iamatest@gmail.com", username="iamatest")
        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"
        self.entries = []

    def update_entries(self):
        self.entries = [Entry.objects.get_or_create(title=self.blog_title + str(index),
                                                    body=self.blog_body + str(index),
                                                    author=self.author)[0]
                        for index in range(30)]

