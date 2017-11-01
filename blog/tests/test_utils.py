# -*- coding: utf-8 -*-
import json
from django.test import TestCase
from unittest.mock import MagicMock, Mock
from blog.utils import ajax_required


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

    def test_is_ajax_false(self):
        """ajax_required decorator called from none ajax client."""

        # Setup.
        attributes = {'is_ajax.return_value': False}
        self.ajax_request.configure_mock(**attributes)

        # Run.
        decorated = ajax_required(self.test_view)
        response = decorated(self.ajax_request)

        # Check.

        # View function was not called.
        self.test_view.assert_not_called()

        # Decorator response.status_code was returned.
        self.assertEqual(response.status_code, 400)

        # Decorator response.content.
        self.assertEqual(json.loads(response.content)['message'], "Bad Request")

    def test_is_ajax_true(self):
        """ajax_required decorator called via ajax."""

        # Setup.
        attributes = {'is_ajax.return_value': True}
        self.ajax_request.configure_mock(**attributes)

        # Run.
        decorated = ajax_required(self.test_view)
        response = decorated(self.ajax_request)

        # Check.
        # View was called.
        self.test_view.assert_called_once_with(self.ajax_request)

        # View function returned response.status_code 200.
        self.assertEqual(response.status_code, 200)

        # View function returned response.content.
        self.assertEqual(response.content, "Am a Mock Response!")

    def test_is_ajax_true_no_func_name(self):
        """ajax_required decorator called via ajax from view
          with no attr __name__.
        """

        # Setup.
        delattr(self.test_view, '__name__')  # Del function __name__
        attributes = {'is_ajax.return_value': True}
        self.ajax_request.configure_mock(**attributes)

        # Run.
        decorated = ajax_required(self.test_view)
        response = decorated(self.ajax_request)

        # Check.
        # View was called.
        self.test_view.assert_called_once_with(self.ajax_request)

        # View function returned response.status_code 200.
        self.assertEqual(response.status_code, 200)

        # View function returned response.content.
        self.assertEqual(response.content, "Am a Mock Response!")

