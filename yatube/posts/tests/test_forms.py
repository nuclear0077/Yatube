import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.user = User.objects.create_user(username='auth')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_auth_user_can_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 2',
            'group': self.group.id,
            'author': self.user,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data
        )
        new_post = Post.objects.get(
            text=form_data['text'],
            group=form_data['group'],
            author=form_data['author'],
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertNotEqual(posts_count, posts_count + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.author, form_data['author'])

    def test_auth_user_can_edit_post(self):
        post = Post.objects.create(
            author=self.user, text='Тестовый пост', group=self.group
        )
        form_data = {
            'text': 'Измененный тестовый пост',
            'group': post.group.id,
            'author': self.user,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[post.id]), data=form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        changed_post = Post.objects.get(id=post.id)
        self.assertNotEqual(post.text, changed_post.text)
        self.assertEqual(changed_post.text, form_data['text'])
        self.assertEqual(changed_post.group, post.group)
        self.assertEqual(changed_post.author, post.author)

    def test_no_auth_can_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост 3',
            'group': self.group.id,
            'author': self.user,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'), data=form_data
        )
        login_url = reverse('users:login')
        new_post_url = reverse('posts:post_create')
        target_url = f'{login_url}?next={new_post_url}'
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, target_url)
        self.assertEqual(post_count, post_count)

    def test_no_auth_user_can_edit_post(self):
        text = 'Тестовый пост'
        self.post = Post.objects.create(
            author=self.user, text=text, group=self.group
        )
        first_post = Post.objects.get(text=text)
        form_data = {
            'text': 'Измененный тестовый пост',
            'group': self.group.id,
            'author': self.user,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', args=[first_post.id]), data=form_data
        )
        login_url = reverse('users:login')
        new_post_url = reverse('posts:post_edit', args=[first_post.id])
        target_url = f'{login_url}?next={new_post_url}'
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        changed_post = Post.objects.filter(text=form_data['text']).first()
        self.assertRedirects(response, target_url)
        self.assertIsNone(changed_post)

    def test_auth_user_can_create_post_with_image(self):
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif', content=small_gif, content_type='image/gif'
        )
        form_data = {
            'text': 'Тестовый пост 3',
            'group': self.group.id,
            'author': self.user,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data
        )
        new_post = Post.objects.get(
            text='Тестовый пост 3',
            group=self.group,
            author=self.user,
            image='posts/small.gif',
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertNotEqual(posts_count, posts_count + 1)
        self.assertEqual(new_post.text, form_data['text'])
        self.assertEqual(new_post.group.id, form_data['group'])
        self.assertEqual(new_post.author, form_data['author'])
        self.assertEqual(new_post.image, f'posts/{uploaded.name}')

    def test_auth_user_can_edit_post_with_image(self):
        post = Post.objects.create(
            author=self.user, text='Тестовый пост 5', group=self.group
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small_second.gif',
            content=small_gif,
            content_type='image/gif',
        )

        form_data = {
            'text': 'Измененный тестовый пост',
            'group': self.group.id,
            'image': uploaded,
            'author': self.user,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[post.id]), data=form_data
        )
        changed_post = Post.objects.get(id=post.id)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(changed_post.text, form_data['text'])
        self.assertEqual(changed_post.group.id, form_data['group'])
        self.assertEqual(changed_post.author, form_data['author'])
        self.assertEqual(changed_post.image, f'posts/{uploaded.name}')

    def test_auth_user_can_added_comment(self):
        post = Post.objects.create(
            author=self.user, text='Тестовый пост 6', group=self.group
        )
        form_data = {'text': 'Тестовый комментарий'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[post.id]), data=form_data
        )
        changed_post = Post.objects.get(id=post.id)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(
            str(changed_post.comments.get()), form_data['text'][:15]
        )
        self.assertEqual(changed_post.text, post.text)
        self.assertEqual(changed_post.group, post.group)
        self.assertEqual(changed_post.author, post.author)
