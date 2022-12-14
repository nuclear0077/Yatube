from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user, text='Тестовый пост', group=cls.group
        )
        cls.ALL_URLS = (
            (''),
            (f'/group/{cls.group.slug}/'),
            (f'/profile/{cls.user}/'),
            (f'/posts/{cls.post.id}/'),
            ('/create/'),
            (f'/posts/{cls.post.id}/edit/'),
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_urls_uses_correct_template_user(self):
        urls_templates_names = (
            (reverse('posts:index'), 'posts/index.html'),
            (
                reverse('posts:group_list', args=[self.group.slug]),
                'posts/group_list.html',
            ),
            (reverse('posts:profile', args=[self.user]), 'posts/profile.html'),
            (
                reverse('posts:post_detail', args=[self.post.id]),
                'posts/post_detail.html',
            ),
            (
                reverse('posts:post_edit', args=[self.post.id]),
                'posts/create_post.html',
            ),
            (reverse('posts:post_create'), 'posts/create_post.html'),
            (reverse('posts:follow_index'), 'posts/follow.html'),
        )
        for address, template in urls_templates_names:
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_access_allowed_urls_user_author(self):
        for url in self.ALL_URLS:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_access_allowed_urls_user_no_author(self):
        new_user = User.objects.create_user(username='auth2')
        no_author = Client()
        no_author.force_login(new_user)
        for url in self.ALL_URLS:
            with self.subTest(url=url):
                response = no_author.get(url)
                if url.endswith('/edit/'):
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_access_allowed_urls_anonym(self):
        for url in self.ALL_URLS:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                if url.endswith('/edit/') or url.endswith('/create/'):
                    self.assertEqual(response.status_code, HTTPStatus.FOUND)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_creating_post_is_user_author(self):
        form_data = {
            'text': 'Тестовый пост для редиректа',
            'group': self.group.id,
            'author': self.user,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data
        )
        self.assertTrue(Post.objects.count() == 2)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, reverse('posts:profile', args=[self.user])
        )

    def test_redirect_creating_post_anonym(self):
        form_data = {
            'text': 'Тестовый пост для редиректа',
            'group': self.group.id,
            'author': self.user,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'), data=form_data
        )
        login_url = reverse('users:login')
        new_post_url = reverse('posts:post_create')
        target_url = f'{login_url}?next={new_post_url}'
        self.assertTrue(Post.objects.count() == 1)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, target_url)

    def test_edit_post_is_user_author(self):
        post_local = Post.objects.create(
            author=self.user,
            text='Пост для проверки редактирования',
            group=self.group,
        )
        form_data = {
            'text': 'Меняем текст',
            'group': post_local.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[post_local.id]), data=form_data
        )
        current_text = Post.objects.get(id=post_local.id).text
        self.assertNotEqual(post_local.text, current_text)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, reverse('posts:post_detail', args=[post_local.id])
        )

    def test_edit_post_is_user_not_author(self):
        new_user = User.objects.create_user(username='auth2')
        no_author = Client()
        no_author.force_login(new_user)
        form_data = {
            'text': 'Меняем текст',
            'group': self.post.group.id,
        }
        response = no_author.post(
            reverse('posts:post_edit', args=[self.post.id]), data=form_data
        )
        current_text = Post.objects.get(id=self.post.id).text
        self.assertTrue(self.post.text == current_text)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, reverse('posts:post_detail', args=[self.post.id])
        )

    def test_edit_post_is_user_anonym(self):
        form_data = {
            'text': 'Меняем текст',
            'group': self.post.group.id,
        }
        response = self.guest_client.post(
            reverse('posts:post_edit', args=[self.post.id]), data=form_data
        )
        login_url = reverse('users:login')
        new_post_url = reverse('posts:post_edit', args=[self.post.id])
        target_url = f'{login_url}?next={new_post_url}'
        current_text = Post.objects.get(id=self.post.id).text
        self.assertTrue(self.post.text == current_text)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, target_url)

    def test_can_added_comments_is_author(self):
        post = Post.objects.create(
            author=self.user, text='Тестовый пост два', group=self.group
        )
        form_data = {'text': 'Тестовый комментарий от автора поста'}
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=[post.id]), data=form_data
        )
        changed_post = Post.objects.get(id=post.id)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, reverse('posts:post_detail', args=[post.id])
        )
        self.assertEqual(
            form_data['text'][:15], str(changed_post.comments.get())
        )

    def test_can_added_comments_is_not_author(self):
        user_local = User.objects.create_user(username='auth_local')
        authorized_client_not_author = Client()
        authorized_client_not_author.force_login(user_local)
        post = Post.objects.create(
            author=self.user, text='Тестовый пост три', group=self.group
        )
        form_data = {'text': 'Тестовый комментарий не от автора поста'}
        response = authorized_client_not_author.post(
            reverse('posts:add_comment', args=[post.id]), data=form_data
        )
        changed_post = Post.objects.get(id=post.id)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(
            response, reverse('posts:post_detail', args=[post.id])
        )
        self.assertEqual(
            form_data['text'][:15], str(changed_post.comments.get())
        )

    def test_can_added_comments_is_anonym(self):
        post = Post.objects.create(
            author=self.user, text='Тестовый пост три', group=self.group
        )
        form_data = {'text': 'Тестовый комментарий от автора поста'}
        response = self.guest_client.post(
            reverse('posts:add_comment', args=[post.id]), data=form_data
        )
        changed_post = Post.objects.get(id=post.id)
        login_url = reverse('users:login')
        new_post_url = reverse('posts:add_comment', args=[post.id])
        target_url = f'{login_url}?next={new_post_url}'
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, target_url)
        self.assertEqual(changed_post.comments.exists(), 0)

    def test_custom_templates_404(self):
        response = self.authorized_client.get('/test/not_found')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/custom_error.html')

    def test_allow_subsribe_anonym(self):
        response = self.guest_client.post(
            reverse('posts:profile_follow', args=[self.user])
        )
        login_url = reverse('users:login')
        new_url = reverse('posts:profile_follow', args=[self.user])
        target_url = f'{login_url}?next={new_url}'
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, target_url)

    def test_allow_unsubsribe_anonym(self):
        response = self.guest_client.post(
            reverse('posts:profile_unfollow', args=[self.user])
        )
        login_url = reverse('users:login')
        new_url = reverse('posts:profile_unfollow', args=[self.user])
        target_url = f'{login_url}?next={new_url}'
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, target_url)

    def test_allow_follow_index_anonym(self):
        response = self.authorized_client.post(reverse('posts:follow_index'))
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_allow_follow_index_anonym(self):
        response = self.guest_client.post(reverse('posts:follow_index'))
        login_url = reverse('users:login')
        new_url = reverse('posts:follow_index')
        target_url = f'{login_url}?next={new_url}'
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertRedirects(response, target_url)


# :TODO тут надо еще добавить проверку редиректа,
# при отписке и подписке, но мб редикрета не будет а будет сообщение,
# предлагаю оставить доработку после изменения поведения при действии
