# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import os
import json
import shutil
import tempfile
from PIL import Image

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import Paginator
from django.urls import reverse
from django.template.loader import get_template
from django.test import RequestFactory
from django.test import TestCase
from django.test.utils import override_settings
from django.utils.safestring import SafeText
from django.utils.six import BytesIO

from blog.models import Entry, Image as ImageModel, Category
from blog.views import EntryListView, JsonSearchView


TEST_LOGIN_URL = "/admin/login/"


TEST_INDEX = {
    "default": {
        "ENGINE": "haystack.backends.whoosh_backend.WhooshEngine",
        "PATH": os.path.join(os.path.dirname(__file__), "test_whoosh_index"),
    }
}


def create_image(
    storage, filename, size=(100, 100), image_mode="RGB", image_format="PNG"
):
    """
    Generate a test image, returning the filename that it was saved as.

    If ``storage`` is ``None``, the BytesIO containing the image data
    will be passed instead.
    """
    data = BytesIO()
    Image.new(image_mode, size).save(data, image_format)
    data.seek(0)
    if not storage:
        return data
    image_file = ContentFile(data.read())
    return storage.save(filename, image_file)


@override_settings(LOGIN_URL=TEST_LOGIN_URL)
class CategoryListViewTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

    def setUp(self):
        self.user, __ = get_user_model().objects.get_or_create(
            email="iamatest@test.com", username="iamatest"
        )
        self.user.set_password("123456")
        self.user.save()
        self.client.login(username="iamatest", password="123456")

        self.url = reverse("category-list")
        self.blog_category_names = ["DevOps", "Sales", "Marketing"]

    def bulk_create_category(self):
        __ = Category.objects.bulk_create(
            [Category(name=name) for name in self.blog_category_names]
        )

    def test_category_list(self):
        self.assertEqual(Category.objects.all().count(), 0)
        self.bulk_create_category()

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertIn("categories", response.context)

        self.assertEqual(Category.objects.all().count(), 3)


@override_settings(LOGIN_URL=TEST_LOGIN_URL)
class CategoryDeleteViewTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

    def setUp(self):
        self.user, __ = get_user_model().objects.get_or_create(
            email="iamatest@test.com", username="iamatest"
        )
        self.user.set_password("123456")
        self.user.save()
        self.client.login(username="iamatest", password="123456")

        self.category = Category.objects.get_or_create(name="Test")[0]

    def test_delete(self):
        category_pk = self.category.pk
        url = reverse("delete-category", args=(self.category.pk,))

        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        with self.assertRaises(Exception) as raised:
            Category.objects.get(pk=category_pk)
        self.assertEqual(Category.DoesNotExist, type(raised.exception))


@override_settings(LOGIN_URL=TEST_LOGIN_URL)
class EntryByCategoryListViewTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

    def setUp(self):
        self.url = reverse("category-list")
        self.blog_category_names = ["DevOps", "Sales", "Marketing"]
        self.user, __ = get_user_model().objects.get_or_create(
            email="iamatest@test.com", username="iamatest"
        )
        self.user.set_password("123456")
        self.user.save()
        self.bulk_create_category()

        __ = Entry.objects.get_or_create(
            title="AM a test post", body="This is a test post", author=self.user
        )

        entries = [
            Entry(
                title="AM a test post " + str(index + 1),
                body="This is a test post",
                author=self.user,
                is_published=True,
                category=Category.objects.last(),
            )
            for index in range(4)
        ]

        [entry.save() for entry in entries]

    def bulk_create_category(self):
        __ = Category.objects.bulk_create(
            [Category(name=name) for name in self.blog_category_names]
        )

    def test_with_no_category(self):
        pk = Category.objects.first().pk
        url = reverse("post-in-category", args=(pk,))

        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertIn("entries", response.context)

        self.assertEquals(response.context["entries"].count(), 0)

    def test_post_in_category(self):
        pk = Category.objects.last().pk
        url = reverse("post-in-category", args=(pk,))
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertIn("entries", response.context)
        self.assertEquals(
            response.context["entries"].count(),
            Entry.objects.select_related("category")
            .filter(category__pk=pk)
            .order_by("pk")
            .count(),
        )


class BlogViewTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

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
        self.generic_template_view_tester("/", "index", "index.html")

    def test_about(self):
        self.generic_template_view_tester("/about/", "about", "about.html")

    def test_feedback_blog(self):
        self.generic_template_view_tester("/blog/", "entry_list", "entry_list.html")

    def test_feedback(self):
        self.generic_template_view_tester("/feedback/", "feedback", "feedback.html")


class EntryViewTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

    def setUp(self):
        user = get_user_model()(email="iamatest@test.com", username="iamatest")
        user.set_password("Passiamatest123")
        user.save()
        self.author = user

        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"
        self.entry = Entry.objects.get_or_create(
            title=self.blog_title,
            body=self.blog_body,
            author=self.author,
            is_published=True,
        )[0]

    def test_basic_view(self):
        self.client.login(username="iamatest", password="Passiamatest123")
        url = self.entry.get_absolute_url()
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_title_in_entry(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertContains(response, self.entry.title)

    def test_body_in_entry(self):
        response = self.client.get(self.entry.get_absolute_url())
        self.assertContains(response, self.entry.body)


class EntryListViewTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

    def setUp(self):
        self.author, auth_created = get_user_model().objects.get_or_create(
            email="iamatest@test.com", username="iamatest"
        )
        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"

    def update_entries(self):
        [
            Entry.objects.get_or_create(
                title=self.blog_title + str(index),
                body=self.blog_body + str(index),
                author=self.author,
                is_published=True,
            )
            for index in range(30)
        ]
        self.entries = Entry.objects.all()

    def test_results_not_found(self):
        url = reverse("entry_list")
        expected_text = "There are currently no articles available to view."
        response = self.client.get(url)
        content = str(response.content)
        self.assertTrue(expected_text, content)

    def test_single_entry(self):
        entry, __ = Entry.objects.get_or_create(
            title=self.blog_title,
            body=self.blog_body,
            author=self.author,
            is_published=True,
        )
        response = self.client.get(reverse("entry_list"))
        self.assertContains(response, entry.title)
        self.assertContains(response, entry.slug)

    def test_multiple_entries(self):
        self.update_entries()
        response = self.client.get(reverse("entry_list"))
        self.assertEquals(
            response.context["entries"].count(), EntryListView.paginate_by
        )


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class JsonSearchViewTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

    def update_entries(self):
        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"
        self.author, auth_created = get_user_model().objects.get_or_create(
            email="iamatest@test.com", username="iamatest"
        )

        [
            Entry.objects.get_or_create(
                title=self.blog_title + str(index),
                body=self.blog_body + str(index),
                author=self.author,
                is_published=True,
            )
            for index in range(30)
        ]
        self.entries = Entry.objects.all()

    def test_build_absolute_uri(self):
        url = reverse("navbar_search")
        query_string = {"q": "django tips 6 get_or_create"}

        request = RequestFactory().get(url, query_string)
        json_search_view = JsonSearchView()
        json_search_view.request = request

        """ Test for when we have just a single page."""
        # Test if we want "" to be returned if only one page exist.
        self.assertEqual(
            len(json_search_view.build_absolute_uri(1, empty_on_1=True)), 0
        )

        # Test if we don't want "" to be returned if only one page exist.
        self.assertGreater(
            len(json_search_view.build_absolute_uri(1, empty_on_1=False)), 1
        )

        # Test runner always use domain name as "testserver", so checking if "http://" in string is sufficient
        self.assertIn(
            "http://", json_search_view.build_absolute_uri(1, empty_on_1=False)
        )

        # Check if URI contains query string
        self.assertIn("?", json_search_view.build_absolute_uri(1, empty_on_1=False))

        # Check is "q" in URL query string
        self.assertIn("q=", json_search_view.build_absolute_uri(1, empty_on_1=False))

        # Check is page in URL query string
        self.assertIn("page=", json_search_view.build_absolute_uri(1, empty_on_1=False))

        """ Test for multiple pages will always return full url even if
            empty_on_1 set to True or False.
        """
        self.assertGreater(
            len(json_search_view.build_absolute_uri(2, empty_on_1=True)), 0
        )
        self.assertGreater(
            len(json_search_view.build_absolute_uri(2, empty_on_1=False)), 0
        )

    def test_build_pager(self):
        url = reverse("navbar_search")
        query_string = {"q": "django tips 6 get_or_create"}

        self.update_entries()
        results = Entry.objects.all().order_by("id")
        results_per_page = results.count() / 2

        paginator = Paginator(results, results_per_page)
        page = paginator.page(1)

        request = RequestFactory().get(
            url, query_string, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        json_search_view = JsonSearchView()
        json_search_view.request = request

        self.assertIsInstance(json_search_view.build_pager(page, paginator), dict)

    def test_create_response(self):
        url = reverse("navbar_search")
        query_string = {"q": "django tips 6 get_or_create"}

        # Make request via ajax.
        response = self.client.get(
            url, query_string, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        self.assertTrue(response.status_code == 200)
        self.assertIsInstance(json.loads(response.content), dict)

    def test_render_json_response(self):
        url = reverse("navbar_search")
        query_string = {"q": "django tips 6 get_or_create"}

        request = RequestFactory().get(
            url, query_string, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )
        json_search_view = JsonSearchView()
        json_search_view.request = request
        response = json_search_view.render_json_response()
        self.assertTrue(response.status_code == 200)
        self.assertIsInstance(json.loads(response.content), dict)


@override_settings(LOGIN_URL=TEST_LOGIN_URL, MEDIA_ROOT=tempfile.gettempdir())
class EntryCreateViewTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

    def setUp(self):
        self.user, __ = get_user_model().objects.get_or_create(
            email="iamatest@test.com", username="iamatest"
        )
        self.user.set_password("123456")
        self.user.save()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(os.path.join(settings.MEDIA_ROOT, "entry"))
        super(EntryCreateViewTestCase, cls).tearDownClass()

    def test_get_on_logged_in_user(self):
        self.client.login(username="iamatest", password="123456")
        url = reverse("entry_create")
        response = self.client.get(url)
        self.assertEqual(str(response.context["user"]), "iamatest")
        self.assertTrue(response.status_code == 200)
        self.assertTemplateUsed(response, "entry_create.html")

    def test_get_on_anonymous_user(self):
        url = reverse("entry_create")
        response = self.client.get(url)
        self.assertTrue(response.status_code == 302)
        self.assertRedirects(
            response,
            "{test_login_url}?next={url}".format(
                test_login_url=TEST_LOGIN_URL, url=url
            ),
        )

    def test_post(self):
        """Test to see normal post."""
        url = reverse("entry_create")
        post_data = {
            "title": "AM a test post",
            "body": "This is a test post",
            "tags": "tags, tester",
        }

        last_total = Entry.objects.all().count()

        self.client.login(username="iamatest", password="123456")

        # Post data
        response = self.client.post(url, data=post_data)

        # Check there was redirect
        self.assertTrue(response.status_code == 302)

        # Check redirected to expected view
        entry = Entry.objects.get(title=post_data["title"])
        self.assertRedirects(response, reverse("entry_update", args=(entry.pk,)))

        # Check new entry was added
        self.assertGreater(Entry.objects.all().count(), last_total)

        # Check if our post is the new one
        self.assertEqual(Entry.objects.last().title, post_data["title"])

        # Check is right user was associated with blog
        self.assertEqual(Entry.objects.get(title=post_data["title"]).author, self.user)

    def test_post_existing_entry(self):
        """Test to see effect of creating an existing entry."""
        url = reverse("entry_create")
        post_data = {"title": "AM a test post", "body": "This is a test post"}

        # Create the entry we will try to recreate again via a post.
        entry = Entry(**post_data)
        entry.author = get_user_model().objects.last()
        entry.save()

        # Get total Entry before we try POST data.
        last_total = Entry.objects.all().count()

        self.client.login(username="iamatest", password="123456")

        # Post data
        response = self.client.post(url, data=post_data)

        # Get the form errors if any and convert to dict.
        form_errors = json.loads(response.content)

        # Check there was no redirect.
        self.assertTrue(response.status_code == 400)

        # Check no new Entry was created.
        self.assertEqual(Entry.objects.all().count(), last_total)

        # Check the title is the/one of the issues.
        self.assertIn("title", form_errors.keys())

        # Check the Entry with title exists.
        self.assertEqual(
            form_errors["title"][0], "Entry with this Title already exists."
        )

    def test_post_empty_data(self):
        """Test to see effects of an empty post data."""
        url = reverse("entry_create")
        post_data = dict()

        # Get total Entry before we try POST data.
        last_total = Entry.objects.all().count()

        # Log user in.
        self.client.login(username="iamatest", password="123456")

        # Post data.
        response = self.client.post(url, data=post_data)

        # Get the form errors if any and convert to dict.
        form_errors = json.loads(response.content)

        # Check there was no redirect.
        self.assertTrue(response.status_code == 400)

        # Check no new Entry was created.
        self.assertEqual(Entry.objects.all().count(), last_total)

        # Check the title is the/one of the issues.
        self.assertIn("title", form_errors.keys())

        # Check the body is the/one of the issues.
        self.assertIn("body", form_errors.keys())

    def test_post_with_poster(self):
        """Test to see normal with poster upload."""
        url = reverse("entry_create")
        post_data = {
            "title": "AM a test post",
            "body": "This is a test post",
            "tags": "test tags, real test tags",
        }

        self.client.login(username="iamatest", password="123456")

        # set up image data
        temp_file = tempfile.NamedTemporaryFile()
        poster = create_image(None, temp_file)
        poster_file = SimpleUploadedFile("poster.png", poster.getvalue())
        post_data["poster"] = poster_file

        # Post data
        response = self.client.post(url, data=post_data, format="multipart")

        entry = Entry.objects.get(title=post_data["title"])

        self.assertIsNotNone(entry.poster)

        # Check there was redirect
        self.assertTrue(response.status_code == 302)

        # Check redirected to expected view
        self.assertRedirects(response, reverse("entry_update", args=(entry.pk,)))


@override_settings(LOGIN_URL=TEST_LOGIN_URL)
class EntryUpdateViewTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

    def setUp(self):
        self.author = get_user_model()(email="iamatest@gmail.com", username="iamatest")
        self.author.set_password("123456")
        self.author.save()

        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"

        self.entry = Entry.objects.get_or_create(
            title=self.blog_title,
            body=self.blog_body,
            author=self.author,
            is_published=True,
        )[0]

    def test_post_update_data(self):
        url = reverse("entry_update", args=(self.entry.pk,))
        post_data = {
            "body": "A new post",
            "title": self.entry.title,
            "tags": "tags, food",
            "is_published": self.entry.is_published,
        }

        self.client.login(username="iamatest", password="123456")

        # Post data
        response = self.client.post(
            url, data=post_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        # Check there was redirect
        self.assertTrue(response.status_code == 302)

        new_entry = Entry.objects.get(pk=self.entry.id)
        self.assertNotEqual(new_entry.body, self.blog_body)

    def test_post_update_empty_data(self):
        url = reverse("entry_update", args=(self.entry.pk,))
        post_data = {}
        body = self.entry.body

        self.client.login(username="iamatest", password="123456")

        # Post data
        response = self.client.post(
            url, data=post_data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        # empty did not override data
        self.assertEqual(Entry.objects.get(pk=self.entry.pk).body, body)

        # Check there was redirect
        self.assertTrue(response.status_code == 200)


@override_settings(LOGIN_URL=TEST_LOGIN_URL, MEDIA_ROOT=tempfile.gettempdir())
class ImageDetailViewTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

    def setUp(self):
        self.author = get_user_model()(email="iamatest@gmail.com", username="iamatest")
        self.author.set_password("123456")
        self.author.save()

        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"

        entry = Entry.objects.get_or_create(
            title=self.blog_title,
            body=self.blog_body,
            author=self.author,
            is_published=True,
        )[0]

        # Create image
        temp_file = tempfile.NamedTemporaryFile()
        image = create_image(None, temp_file)
        uploaded_image = SimpleUploadedFile("image.png", image.getvalue())

        image = ImageModel(
            caption="Am a test image", entry=entry, photo=uploaded_image.name
        )
        image.save()

        self.client.login(username="iamatest", password="123456")

    def test_get(self):
        image = ImageModel.objects.last()
        response = self.client.get(
            image.get_absolute_url(), HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        # Check there was redirect
        self.assertTrue(response.status_code == 200)

        # Check there was redirect
        self.assertIsInstance(response.json(), dict)


@override_settings(LOGIN_URL=TEST_LOGIN_URL, MEDIA_ROOT=tempfile.gettempdir())
class ImageCreateViewTestCase(TestCase):
    def tearDown(self):
        from django_redis import get_redis_connection

        get_redis_connection("default").flushall()

    def setUp(self):
        self.author = get_user_model()(email="iamatest@gmail.com", username="iamatest")
        self.author.set_password("123456")
        self.author.save()

        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"

        self.entry = Entry.objects.get_or_create(
            title=self.blog_title,
            body=self.blog_body,
            author=self.author,
            is_published=True,
        )[0]

        # set up image data
        temp_file = tempfile.NamedTemporaryFile()
        uploaded_image = create_image(None, temp_file)
        self.uploaded_image = SimpleUploadedFile(
            "poster.png", uploaded_image.getvalue()
        )

        self.client.login(username="iamatest", password="123456")

    def test_post(self):
        data = dict(
            caption="Am a test image", entry=self.entry.pk, photo=self.uploaded_image
        )
        response = self.client.post(
            reverse("image_create"), data, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
        )

        # Check there was redirect
        self.assertTrue(response.status_code == 201)

        # Check there was redirect
        self.assertIsInstance(response.json(), dict)
