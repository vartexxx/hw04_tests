from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug-for-test',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка создания новой записи"""
        posts_count = Post.objects.count()
        post_form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id,
            'author': self.user,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=post_form_data,
            follow=True
        )
        last_post = Post.objects.all().last()
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertEqual(last_post.text, 'Тестовый пост')
        self.assertEqual(last_post.group, self.group)
        self.assertEqual(last_post.author, self.user)

    def test_edit_post(self):
        """Проверка редактирования записи"""
        post_edit_form_data = {
            'text': 'Изменённый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=post_edit_form_data,
            follow=True
        )
        last_post = Post.objects.all().last()
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': last_post.id}
            )
        )
        self.assertEqual(last_post.text, 'Изменённый текст')
        self.assertEqual(last_post.group, self.group)
