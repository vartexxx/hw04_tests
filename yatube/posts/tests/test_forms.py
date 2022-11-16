from django import forms
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group, User

USERNAME = 'user'
SLUG_1 = 'slug-one'
SLUG_2 = 'slug-two'

POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[USERNAME])


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
            text='Тестовый пост 1',
            group=cls.group_1,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])
        cls.posts_initially = Post.objects.count()

    def setUp(self) -> None:
        self.another = Client()
        self.another.force_login(self.user)

    def test_create_post(self):
        """Проверка создания новой записи"""
        posts_before_create_new = set(Post.objects.all())
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group_1.id,
        }
        response = self.another.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        self.assertEqual(
            Post.objects.count(),
            self.posts_initially + 1
        )
        created_posts = set(Post.objects.all()) - posts_before_create_new
        self.assertEqual(len(created_posts), 1)
        post = created_posts.pop()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.user)
        self.assertRedirects(response, PROFILE_URL)

    def test_edit_post(self):
        """Проверка редактирования записи"""
        form_data = {
            'text': 'Изменённый текст 123',
            'group': self.group_2.id,
        }
        response = self.another.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        post = response.context['post']
        self.assertRedirects(response, self.POST_DETAIL_URL)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.author, self.post.author)

    def test_create_post_page_show_correct_context(self):
        """
        Шаблон create_post при создании поста сформирован
        с правильным контекстом.
        """
        response = self.another.get(POST_CREATE_URL)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
