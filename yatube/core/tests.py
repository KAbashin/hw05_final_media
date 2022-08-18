from django.test import TestCase
from http import HTTPStatus


class ViewTestClass(TestCase):
    def test_error_page(self):
        response = self.client.get('/nonexist-page/')
        expected_status_code = HTTPStatus.NOT_FOUND
        expected_template = 'core/404.html'
        self.assertEqual(response.status_code, expected_status_code)
        self.assertTemplateUsed(response, expected_template)
