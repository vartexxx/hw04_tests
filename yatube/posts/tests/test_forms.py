from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='slug-for-test_1',
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='slug-for-test_2',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group_1,
        )
        cls.posts_initially = Post.objects.count()

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка создания новой записи"""
        post_before_create = set(Post.objects.all())
        post_form_data = {
            'text': 'Тестовый пост',
            'group': self.group_1.id,
        }
        self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            self.posts_initially + 1
        )
        created_posts = set(Post.objects.all()) - post_before_create
        post = Post.objects.get(id=1)
        self.assertTrue(len(created_posts) == 1)
        self.assertEqual(
            post.text,
            post_form_data['text']
        )
        self.assertEqual(
            post.group.id,
            post_form_data['group']
        )

    def test_edit_post(self):
        """Проверка редактирования записи"""
        post_edit_form_data = {
            'text': 'Изменённый текст',
            'group': self.group_2.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=post_edit_form_data,
            follow=True
        )
        post_edited = Post.objects.get(id=self.post.id)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                args=[post_edited.id]
            )
        )
        self.assertEqual(
            post_edited.text,
            post_edit_form_data['text']
        )
        self.assertEqual(
            post_edited.group.id,
            post_edit_form_data['group']
        )

    def test_create_post_page_show_correct_context(self):
        """
        Шаблон create_post при создании поста сформирован
        с правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:post_create'
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
