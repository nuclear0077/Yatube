from django.test import Client, TestCase
from django.urls import reverse


class StaticTemplateTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_templates_used(self):
        urls_templates = (
            (reverse('about:author'), 'about/author.html'),
            (reverse('about:tech'), 'about/tech.html'),
        )
        for url, template in urls_templates:
            with self.subTest(url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)
