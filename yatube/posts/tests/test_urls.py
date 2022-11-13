from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group

User = get_user_model()


class PostsURLTests(TestCase):
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

    def setUp(self) -> None:
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author_client = Client()
        self.author_client.force_login(self.user_author)

    def test_urls_exists_at_desired_location_for_geusts(self):
        """Страницы доступны для неавторизованных пользователей"""
        urls_collection = {
            reverse(
                'posts:index'
            ): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ):
                HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author.username}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.FOUND,
            reverse(
                'posts:post_create'
            ): HTTPStatus.FOUND,
            '/non_existing_page/': HTTPStatus.NOT_FOUND
        }

        for url, http_status in urls_collection.items():
            with self.subTest(address=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, http_status)

    def test_urls_exists_at_desired_location_for_authors(self):
        """Страницы доступны для авторов"""
        urls_collection = {
            reverse(
                'posts:index'
            ): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ):
                HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author.username}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_create'
            ): HTTPStatus.OK,
            '/non_existing_page/': HTTPStatus.NOT_FOUND
        }
        for url, http_status in urls_collection.items():
            with self.subTest(address=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, http_status)

    def test_urls_exists_at_desired_location_for_users(self):
        """Страницы доступны для авторизованных пользователей"""
        urls_collection = {
            reverse(
                'posts:index'
            ): HTTPStatus.OK,
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ):
                HTTPStatus.OK,
            reverse(
                'posts:profile',
                kwargs={'username': self.user_author.username}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.OK,
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): HTTPStatus.FOUND,
            reverse(
                'posts:post_create'
            ): HTTPStatus.OK,
            '/non_existing_page/': HTTPStatus.NOT_FOUND
        }
        for url, http_status in urls_collection.items():
            with self.subTest(address=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, http_status)
