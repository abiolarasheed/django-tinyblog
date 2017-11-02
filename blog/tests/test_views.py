# -*- coding: utf-8 -*-
import os
import json

from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.template.loader import get_template
from django.test import RequestFactory
from django.test import TestCase
from django.test.utils import override_settings
from django.urls.base import reverse
from django.utils.safestring import SafeText

from blog.models import Entry
from blog.views import EntryCreateView, EntryListView, JsonSearchView


TEST_INDEX = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(os.path.dirname(__file__), 'test_whoosh_index'),
    },
}


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
            objects.get_or_create(email="iamatest@test.com", username="iamatest")
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
            objects.get_or_create(email="iamatest@test.com", username="iamatest")
        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"

    def update_entries(self):
        [Entry.objects.get_or_create(title=self.blog_title + str(index),
                                     body=self.blog_body + str(index),
                                     author=self.author, is_published=True)
         for index in range(30)]
        self.entries = Entry.objects.all()

    def test_results_not_found(self):
        url = reverse('entry_list')
        response = self.client.get(url)
        self.assertContains(response, 'Results Not Found.')

    def test_single_entry(self):
        entry, __ = Entry.objects.get_or_create(title=self.blog_title,
                                                body=self.blog_body,
                                                author=self.author,
                                                is_published=True)
        response = self.client.get(reverse('entry_list'))
        self.assertContains(response, entry.title)
        self.assertContains(response, entry.slug)

    def test_multiple_entries(self):
        self.update_entries()
        response = self.client.get(reverse('entry_list'))
        self.assertEquals(response.context['entries'].count(),
                          EntryListView.paginate_by)


@override_settings(HAYSTACK_CONNECTIONS=TEST_INDEX)
class JsonSearchViewTestCase(TestCase):
    def update_entries(self):
        self.blog_title = "Test blog Title"
        self.blog_body = "This is my test blog"
        self.author, auth_created = get_user_model().\
            objects.get_or_create(email="iamatest@test.com", username="iamatest")

        [Entry.objects.get_or_create(title=self.blog_title + str(index),
                                     body=self.blog_body + str(index),
                                     author=self.author, is_published=True)
         for index in range(30)]
        self.entries = Entry.objects.all()

    def test_build_absolute_uri(self):
        url = reverse('navbar_search')
        query_string = {'q': 'django tips 6 get_or_create'}

        request = RequestFactory().get(url, query_string)
        json_search_view = JsonSearchView()
        json_search_view.request = request

        """ Test for when we have just a single page."""
        # Test if we want "" to be returned if only one page exist.
        self.assertEqual(len(json_search_view.build_absolute_uri(1, empty_on_1=True)), 0)

        # Test if we don't want "" to be returned if only one page exist.
        self.assertGreater(len(json_search_view.build_absolute_uri(1, empty_on_1=False)), 1)

        # Test runner always use domain name as "testserver", so checking if "http://" in string is sufficient
        self.assertIn('http://', json_search_view.build_absolute_uri(1, empty_on_1=False))

        # Check if URI contains query string
        self.assertIn('?', json_search_view.build_absolute_uri(1, empty_on_1=False))

        # Check is "q" in URL query string
        self.assertIn('q=', json_search_view.build_absolute_uri(1, empty_on_1=False))

        # Check is page in URL query string
        self.assertIn('page=', json_search_view.build_absolute_uri(1, empty_on_1=False))

        """ Test for multiple pages will always return full url even if
            empty_on_1 set to True or False.
        """
        self.assertGreater(len(json_search_view.build_absolute_uri(2, empty_on_1=True)), 0)
        self.assertGreater(len(json_search_view.build_absolute_uri(2, empty_on_1=False)), 0)

    def test_build_pager(self):
        url = reverse('navbar_search')
        query_string = {'q': 'django tips 6 get_or_create'}

        self.update_entries()
        results = Entry.objects.all().order_by('id')
        results_per_page = results.count() / 2

        paginator = Paginator(results, results_per_page)
        page = paginator.page(1)

        request = RequestFactory().get(url, query_string)
        json_search_view = JsonSearchView()
        json_search_view.request = request

        self.assertIsInstance(json_search_view.build_pager(page, paginator), dict)

    def test_create_response(self):
        url = reverse('navbar_search')
        query_string = {'q': 'django tips 6 get_or_create'}

        # Make request via ajax.
        response = self.client.get(url, query_string,
                                   HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertTrue(response.status_code == 200)
        self.assertIsInstance(json.loads(response.content), dict)

    def test_render_json_response(self):
        url = reverse('navbar_search')
        query_string = {'q': 'django tips 6 get_or_create'}

        request = RequestFactory().get(url, query_string,
                                       HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        json_search_view = JsonSearchView()
        json_search_view.request = request
        response = json_search_view.render_json_response()
        self.assertTrue(response.status_code == 200)
        self.assertIsInstance(json.loads(response.content), dict)


class EntryCreateViewTestCase(TestCase):
    pass
