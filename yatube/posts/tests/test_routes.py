from django.test import TestCase, Client
from django.urls import resolve, reverse

from ..models import Post, Group, User

SLUG_FOR_TEST = 'slug-for-test'
USERNAME_FOR_TEST = 'user'

templates_urls = {
    'posts:index': {
        'reverse': reverse('posts:index'),
        'url': '/'
    },
    'posts:group_list': {
        'reverse': reverse('posts:group_list', args=[SLUG_FOR_TEST]),
        'url': f'/group/{SLUG_FOR_TEST}/'
    },
    'posts:profile': {
        'reverse': reverse('posts:profile', args=[USERNAME_FOR_TEST]),
        'url': f'/profile/{USERNAME_FOR_TEST}/'
    },
    'posts:post_create': {
        'reverse': reverse('posts:post_create'),
        'url': '/create/'
    },
}


class RoutesTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.user_author = User.objects.create_user(username='author')
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug-for-test',
            description='Тестовое описание',
        )
        templates_urls['posts:post_detail'] = {
            'reverse': reverse('posts:post_detail', args=[cls.post.id]),
            'url': f'/posts/{cls.post.id}/'
        }
        templates_urls['posts:post_edit'] = {
            'reverse': reverse('posts:post_edit', args=[cls.post.id]),
            'url': f'/posts/{cls.post.id}/edit/'
        }

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_routes(self):
        """Проверка ожидаемых маршрутов URL"""
        for namespace, key in templates_urls.items():
            with self.subTest(view=namespace, url=key['url']):
                self.assertEqual(
                    resolve(key['url']).view_name,
                    namespace
                )
