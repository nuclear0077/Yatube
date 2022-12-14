from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_user(self):
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Тестовый пользователь',
            'last_name': 'Тестовая фамилия',
            'username': 'test_user',
            'email': 'test@mail.ru',
            'password1': '123412341234q!',
            'password2': '123412341234q!',
        }
        self.guest_client.post(reverse('users:signup'), data=form_data)
        self.assertEqual(User.objects.count(), users_count + 1)
