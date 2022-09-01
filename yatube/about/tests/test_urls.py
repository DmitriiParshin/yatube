from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse


class AboutPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_pages(self):
        names = ('about:author', 'about:tech')
        for name in names:
            with self.subTest():
                response = self.guest_client.get(reverse(name))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_about_reverse_names(self):
        names_templates = (
            ('about:author', '/about/author/'),
            ('about:tech', '/about/tech/'),
        )
        for name, template in names_templates:
            with self.subTest():
                self.assertEqual(reverse(name), template)
