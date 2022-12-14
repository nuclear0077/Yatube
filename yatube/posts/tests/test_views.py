import shutil
import tempfile
from http import HTTPStatus

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif', content=cls.small_gif, content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_uses_correct_template(self):
        urls_templates_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', args=['test-slug']
            ): 'posts/group_list.html',
            reverse('posts:profile', args=['auth']): 'posts/profile.html',
            reverse('posts:post_detail', args=[1]): 'posts/post_detail.html',
            reverse('posts:post_edit', args=[1]): 'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for address, template in urls_templates_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_main_page_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group.title, 'Тестовая группа')
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.group.slug, 'test-slug')

    def test_group_list_page_context(self):
        response_first = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        self.assertIn('group', response_first.context)
        group_object = response_first.context['group']
        self.assertEqual(group_object.title, 'Тестовая группа')
        self.assertEqual(group_object.slug, 'test-slug')
        self.assertIn('page_obj', response_first.context)
        first_object = response_first.context['page_obj'][0]
        self.assertEqual(first_object.text, 'Тестовый пост')

    def test_profile_page_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', args=[self.user])
        )
        self.assertIn('page_obj', response.context)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.group.title, 'Тестовая группа')
        self.assertEqual(first_object.text, 'Тестовый пост')
        self.assertEqual(first_object.group.slug, 'test-slug')
        self.assertEqual(response.context['author'], self.user)

    def test_post_detail_context(self):
        """Функция для проверки context страницы поста"""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        self.assertIn('post', response.context)
        post_object = response.context['post']
        self.assertEqual(post_object.group.title, 'Тестовая группа')
        self.assertEqual(post_object.text, 'Тестовый пост')
        self.assertEqual(post_object.group.slug, 'test-slug')

    def test_form_edit_post(self):
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[self.post.id])
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        self.assertIn('is_edit', response.context)
        prefix_object = response.context['is_edit']
        self.assertTrue(prefix_object)
        self.assertIsInstance(prefix_object, bool)
        self.assertIn('form', response.context)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_form_create_post(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        self.assertIn('form', response.context)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_additional_check_when_setting_post(self):
        response_dict = {
            'index': self.authorized_client.get(reverse('posts:index')),
            'group': self.authorized_client.get(
                reverse('posts:group_list', args=[self.group.slug])
            ),
            'profile': self.authorized_client.get(
                reverse('posts:profile', args=[self.user])
            ),
        }
        for slug, response in response_dict.items():
            with self.subTest():
                self.assertIn('page_obj', response.context)
                self.assertEqual(
                    response.context['page_obj'][0].group.title,
                    'Тестовая группа',
                )
                self.assertEqual(
                    response.context['page_obj'][0].text, 'Тестовый пост'
                )
                self.assertEqual(
                    response.context['page_obj'][0].group.slug, 'test-slug'
                )

    def test_checking_if_a_post_is_in_another_group(self):
        group_second = Group.objects.create(
            title='Тестовая группа два',
            slug='test-slug-two',
            description='Тестовое описание группы second',
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[group_second.slug])
        )
        self.assertIn('page_obj', response.context)
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_main_page_context_with_image(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn('page_obj', response.context)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.image, 'posts/small.gif')

    def test_group_list_page_context_with_image(self):
        response_first = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        self.assertIn('page_obj', response_first.context)
        first_object = response_first.context['page_obj'][0]
        self.assertEqual(first_object.image, 'posts/small.gif')

    def test_profile_page_context_with_image(self):
        response = self.authorized_client.get(
            reverse('posts:profile', args=[self.user])
        )
        self.assertIn('page_obj', response.context)
        first_object = response.context['page_obj'][0]
        self.assertEqual(first_object.image, 'posts/small.gif')

    def test_post_detail_context_with_image(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        self.assertIn('post', response.context)
        post_object = response.context['post']
        self.assertEqual(post_object.image, 'posts/small.gif')

    def test_subsribe_auth(self):
        user_following = User.objects.create_user(username='auth2')
        authorized_client_following = Client()
        authorized_client_following.force_login(user_following)
        user_follower_count = self.user.follower.count()
        response = authorized_client_following.post(
            reverse('posts:profile_follow', args=[self.user])
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(self.user.following.count(), user_follower_count + 1)

    def test_unsubsribe_auth(self):
        user_following = User.objects.create_user(username='auth2')
        authorized_client_following = Client()
        authorized_client_following.force_login(user_following)
        response = authorized_client_following.post(
            reverse('posts:profile_follow', args=[self.user])
        )
        user_follower_count = self.user.following.count()
        response_second = authorized_client_following.post(
            reverse('posts:profile_unfollow', args=[self.user])
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(response_second.status_code, HTTPStatus.FOUND)
        self.assertEqual(self.user.following.count(), user_follower_count - 1)

    def test_favorite_posts(self):
        user_following = User.objects.create_user(username='auth_second')
        authorized_client_following = Client()
        authorized_client_following.force_login(user_following)
        subscribe_response_first = self.authorized_client.post(
            reverse('posts:profile_follow', args=[user_following])
        )
        self.assertEqual(
            subscribe_response_first.status_code, HTTPStatus.FOUND
        )
        subscribe_response_second = authorized_client_following.post(
            reverse('posts:profile_follow', args=[self.user])
        )
        self.assertEqual(
            subscribe_response_second.status_code, HTTPStatus.FOUND
        )
        response_first = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response_first.status_code, HTTPStatus.OK)
        response_second = authorized_client_following.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response_second.status_code, HTTPStatus.OK)
        content_first = response_first.content
        content_second = response_second.content
        self.assertNotEqual(content_first, content_second)
        post_count_all = Post.objects.count()
        Post.objects.create(
            author=self.user, text='Тестовый пост', group=self.group
        )
        self.assertEqual(Post.objects.count(), post_count_all + 1)
        response_threeth = self.authorized_client.get(
            reverse('posts:follow_index')
        )
        response_fourth = authorized_client_following.get(
            reverse('posts:follow_index')
        )
        content_threeth = response_threeth.content
        content_fourth = response_fourth.content
        self.assertNotEqual(content_second, content_fourth)
        self.assertEqual(content_first, content_threeth)

    def test_comments_in_page(self):
        post = Post.objects.create(
            author=self.user, text='Тестовый пост два', group=self.group
        )
        form_data = {'text': 'Тестовый комментарий от автора поста'}
        response_post = self.authorized_client.post(
            reverse('posts:add_comment', args=[post.id]), data=form_data
        )
        self.assertEqual(response_post.status_code, HTTPStatus.FOUND)
        response_get = self.authorized_client.get(
            reverse('posts:post_detail', args=[post.id])
        )
        self.assertIn('comments', response_get.context)
        self.assertEqual(len(response_get.context['comments']), 1)
        self.assertEqual(
            response_get.context['comments'][0], post.comments.get()
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        Post.objects.bulk_create(
            Post(author=cls.user, text=f'Тестовый пост {i}', group=cls.group)
            for i in range(13)
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_page_contains_records(self):
        COUNT_POSTS = 3
        list_urls = (
            ('posts:index', None, None, settings.LIMIT_POSTS),
            (
                'posts:group_list',
                [self.group.slug],
                None,
                settings.LIMIT_POSTS,
            ),
            ('posts:profile', [self.user], None, settings.LIMIT_POSTS),
            ('posts:group_list', [self.group.slug], {'page': 2}, COUNT_POSTS),
        )
        for url, args, page, expected_values in list_urls:
            with self.subTest(url=url):
                response = self.guest_client.get(reverse(url, args=args), page)
                self.assertIn('page_obj', response.context)
                self.assertEqual(
                    len(response.context['page_obj'].object_list),
                    expected_values,
                )


class PostCacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user, text='Тестовый пост', group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_the_cache(self):
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост для проверки кэша',
            group=self.group,
        )
        response_first = self.authorized_client.get(reverse('posts:index'))
        first_object = response_first.content
        Post.objects.get(id=post.id).delete()
        self.assertFalse(Post.objects.filter(id=post.id).exists())
        response_second = self.authorized_client.get(reverse('posts:index'))
        second_object = response_second.content
        self.assertEqual(first_object, second_object)
        cache.clear()
        response_third = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(second_object, response_third)
