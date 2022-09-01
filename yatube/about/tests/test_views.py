from django.test import Client, TestCase
from django.urls import reverse


class AboutPagesTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_pages_uses_correct_template(self):
        templates_pages_names = (
            ('about:author', 'about/author.html'),
            ('about:tech', 'about/tech.html'),
        )
        for name, template in templates_pages_names:
            with self.subTest():
                response = self.client.get(reverse(name))
                self.assertTemplateUsed(response, template)
