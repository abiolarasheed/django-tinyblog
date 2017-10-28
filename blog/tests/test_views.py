# -*- coding: utf-8 -*-
from django.test import TestCase, RequestFactory
from django.urls.base import reverse
from django.template.loader import get_template
from django.utils.safestring import SafeText


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
