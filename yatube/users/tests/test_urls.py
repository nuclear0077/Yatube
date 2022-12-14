from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_templates_no_auth(self):
        """Функция для проверки загрузки шаблонов urls без авторизации"""
        address_templates = {
            reverse('users:logout'): 'users/logged_out.html',
            reverse('users:login'): 'users/login.html',
            reverse(
                'users:password_reset_form'
            ): 'users/password_reset_form.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
            reverse(
                'users:passowrd_reset_confirm', args=['Mw', '64v-80f6687']
            ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
        }
        for address, template in address_templates.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_templates_auth(self):
        address_templates = {
            reverse('users:password_change'): 'users/password_change_form.html'
        }
        for address, template in address_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_redirect_no_auth(self):
        login_url = reverse('users:login')
        new_post_url = reverse('users:password_change')
        target_url = f'{login_url}?next={new_post_url}'
        urls_redirect = {reverse('users:password_change'): target_url}
        for address, redirect_address in urls_redirect.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertRedirects(response, redirect_address)

    def test_access_allowed_urls_no_auth(self):
        urls_access = {
            reverse('users:logout'): HTTPStatus.OK,
            reverse('users:login'): HTTPStatus.OK,
            reverse('users:password_reset_form'): HTTPStatus.OK,
            reverse('users:password_change_done'): HTTPStatus.OK,
            reverse(
                'users:passowrd_reset_confirm', args=['Mw', '64v-80f6687']
            ): HTTPStatus.OK,
            reverse('users:password_reset_complete'): HTTPStatus.OK,
        }
        for address, status in urls_access.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address, follow=True)
                self.assertEqual(response.status_code, status)

    def test_access_allowed_urls_auth(self):
        urls_access = {reverse('users:password_change'): HTTPStatus.OK}
        for address, status in urls_access.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address, follow=True)
                self.assertEqual(response.status_code, status)
