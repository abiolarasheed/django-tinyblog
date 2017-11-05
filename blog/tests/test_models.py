# -*- coding: utf-8 -*-
import os
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.test.utils import override_settings

from ..models import Entry, Image


class BlogModelTestCase(TestCase):
    def setUp(self):
        self.author, auth_created = get_user_model().\
            objects.get_or_create(email="iamatest@gmail.com", username="iamatest")
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

    def test_get_absolute_url(self):
        entry = self.get_entry()[0]
        self.assertIsNotNone(entry.get_absolute_url())

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

    def test_as_json(self):
        entry = self.get_entry()[0]
        self.assertTrue(hasattr(entry, 'as_json'))
        self.assertIsInstance(entry.as_json(), dict)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class ImageModelTestCase(TestCase):
    def setUp(self):
        self.author, auth_created = get_user_model().\
            objects.get_or_create(email="iamatest@gmail.com", username="iamatest")
        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, 'entry'))
        super(ImageModelTestCase, cls).tearDownClass()

    def get_entry(self):
        return Entry.objects.get_or_create(title=self.blog_title,
                                           body=self.blog_body,
                                           author=self.author,
                                           is_published=True)[0]

    def get_image(self):
        from .test_views import create_image
        temp_file = tempfile.NamedTemporaryFile()
        image = create_image(None, temp_file)
        uploaded_image = SimpleUploadedFile('image.png', image.getvalue())
        return uploaded_image

    def test_create(self):
        entry = self.get_entry()
        image_obj = self.get_image()

        image = Image(caption='Am a test image',
                      entry=entry, photo=image_obj.name)
        image.save()

        self.assertIsInstance(image, Image)
        self.assertIsNotNone(image.photo)
