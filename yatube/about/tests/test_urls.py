from http import HTTPStatus

from django.test import Client, TestCase


class StaticURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_accessibility(self):
        urls_access = (
            '/about/author/',
            '/about/tech/',
        )
        for url in urls_access:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
