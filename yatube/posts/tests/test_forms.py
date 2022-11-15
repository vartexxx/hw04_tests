from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User

USERNAME = 'user'
SLUG_1 = 'slug-one'
SLUG_2 = 'slug-two'

POST_CREATE_URL = reverse('posts:post_create')


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group_1 = Group.objects.create(
            title='Тестовая группа 1',
            slug=SLUG_1,
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug=SLUG_2,
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group_1,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.PROFILE_URL = reverse('posts:profile', args=[cls.post.author])
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
            'author': self.post.author,
        }
        response = self.authorized_client.post(
            POST_CREATE_URL,
            data=post_form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            self.posts_initially + 1
        )
        created_posts = set(Post.objects.all()) - post_before_create
        self.assertEqual(len(created_posts), 1)
        self.assertEqual(
            Post.objects.get(id=self.post.id).text,
            post_form_data['text']
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).group.id,
            post_form_data['group']
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).author,
            post_form_data['author']
        )
        self.assertRedirects(response, self.PROFILE_URL)

    def test_edit_post(self):
        """Проверка редактирования записи"""
        post_edit_form_data = {
            'text': 'Изменённый текст',
            'group': self.group_2.id,
            'author': self.post.author
        }
        response = self.authorized_client.post(
            self.POST_EDIT_URL,
            data=post_edit_form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(
            Post.objects.get(id=self.post.id).text,
            post_edit_form_data['text']
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).group.id,
            post_edit_form_data['group']
        )
        self.assertEqual(
            Post.objects.get(id=self.post.id).author,
            post_edit_form_data['author']
        )

    def test_create_post_page_show_correct_context(self):
        """
        Шаблон create_post при создании поста сформирован
        с правильным контекстом.
        """
        response = self.authorized_client.get(POST_CREATE_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
