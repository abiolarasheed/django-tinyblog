# -*- coding: utf-8 -*-
from django.test import TestCase
from unittest.mock import MagicMock, Mock


class AjaxRequiredTestCase(TestCase):
    def setUp(self):
        # Create the http request object.
        self.ajax_request = Mock()

        # Create the http response object then add the status_code and content.
        self.request_response = Mock()
        self.request_response.status_code = 200
        self.request_response.content = "Am a Mock Response!"

        # Set the view to return the response object.
        self.test_view = MagicMock(return_value=self.request_response)

        # Add the __name__ and __doc__ to view function.
        self.test_view.__doc__ = """Doc for my test view."""
        self.test_view.__name__ = 'test_view'
