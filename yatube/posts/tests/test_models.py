from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Follow, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(author=cls.user, text='1' * 20)

    def test_models_have_correct_object_names(self):
        model_test = (
            (PostModelTest.group, '<Группа: Тестовая группа>'),
            (PostModelTest.post, self.post.text[:15]),
        )
        for obj, expected_value in model_test:
            with self.subTest(obj):
                self.assertEqual(str(obj), expected_value)

    def test_verbose_name(self):
        field_verboses = (
            ('text', 'Текст статьи'),
            ('pub_date', 'Дата публикации'),
            ('author', 'Автор'),
            ('group', 'Группа'),
        )
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).verbose_name,
                    expected_value,
                )

    def test_help_text(self):
        field_help_text = (
            ('text', 'Введите текст статьи'),
            ('group', 'Выберите группу из списка или оставьте поле пустым'),
        )
        for field, help_text in field_help_text:
            with self.subTest(field=field):
                self.assertEqual(
                    self.post._meta.get_field(field).help_text, help_text
                )

    def test_text_cropping_for_post(self):
        init_text = 'Проверяем срез текста до 15 символов'
        post_test = Post.objects.create(
            author=self.user, text=init_text, group=self.group
        )
        self.assertEqual(str(post_test), init_text[: settings.LIMIT_TEXT])


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(
            str(GroupModelTest.group), '<Группа: Тестовая группа>'
        )

    def test_verbose_name(self):
        field_verboses = (
            ('title', 'Заголовок группы'),
            ('slug', 'Имя группы в формате  slug'),
            ('description', 'Описание группы'),
        )
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    self.group._meta.get_field(field).verbose_name,
                    expected_value,
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(author=cls.user, text='1' * 20)
        cls.cooment = Comment.objects.create(
            post=cls.post, author=cls.user, text='Текст комментария'
        )

    def test_models_have_correct_object_names(self):
        self.assertEqual(self.cooment.text[:15], str(self.cooment))

    def test_verbose_name(self):
        field_verboses = (
            ('post', 'Пост к которому написан комментарий'),
            ('author', 'Автор'),
            ('text', 'Текст комментария'),
            ('created', 'Дата публикации'),
        )
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    self.cooment._meta.get_field(field).verbose_name,
                    expected_value,
                )


class FollowModelTest(TestCase):
    def test_verbose_name(self):
        field_verboses = (
            ('user', 'Подписчик'),
            ('author', 'Авторы на которых подписываются'),
        )
        for field, expected_value in field_verboses:
            with self.subTest(field=field):
                self.assertEqual(
                    Follow._meta.get_field(field).verbose_name, expected_value
                )
