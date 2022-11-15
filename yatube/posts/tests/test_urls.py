from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User

USERNAME = 'user'
USERNAME_AUTHOR = 'author'
SLUG_FOR_TEST = 'slug-for-test'

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL = reverse('posts:group_list', args=[SLUG_FOR_TEST])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])
POST_CREATE_URL = reverse('posts:post_create')
LOGIN = reverse('users:login')
NON_EXISTING_PAGE_URL = '/non_existing_page/'


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username=USERNAME)
        cls.user_author = User.objects.create_user(username=USERNAME_AUTHOR)
        cls.post = Post.objects.create(
            author=cls.user_author,
            text='Тестовый пост',
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG_FOR_TEST,
            description='Тестовое описание',
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    def setUp(self) -> None:
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

        self.author_client = Client()
        self.author_client.force_login(self.user_author)

    def test_posts_urls_correct_status_code(self):
        """
        Проверка доступа к URL различного уровня
        авторизации пользователей.
        """
        urls = [
            [INDEX_URL, self.guest_client, HTTPStatus.OK],
            [GROUP_LIST_URL, self.guest_client, HTTPStatus.OK],
            [PROFILE_URL, self.guest_client, HTTPStatus.OK],
            [self.POST_DETAIL_URL, self.guest_client, HTTPStatus.OK],
            [NON_EXISTING_PAGE_URL, self.guest_client, HTTPStatus.NOT_FOUND],
            [POST_CREATE_URL, self.guest_client, HTTPStatus.FOUND],
            [self.POST_EDIT_URL, self.guest_client, HTTPStatus.FOUND],
            [self.POST_EDIT_URL, self.author_client, HTTPStatus.OK],
            [self.POST_EDIT_URL, self.authorized_client, HTTPStatus.FOUND],
            [POST_CREATE_URL, self.authorized_client, HTTPStatus.OK],
        ]
        for url, client, status in urls:
            with self.subTest(url=url):
                self.assertEqual(
                    client.get(url).status_code,
                    status
                )

    def test_posts_urls_correct_redirect(self):
        """Проверка редиректов со страниц."""
        redirect_urls = [
            [
                POST_CREATE_URL,
                self.guest_client,
                f'{LOGIN}?next={POST_CREATE_URL}'
            ],
            [
                self.POST_EDIT_URL,
                self.guest_client,
                f'{LOGIN}?next={self.POST_EDIT_URL}'
            ],
            [
                self.POST_EDIT_URL,
                self.authorized_client,
                self.POST_DETAIL_URL
            ],
        ]
        for url, client, redirect in redirect_urls:
            with self.subTest(url=url):
                self.assertRedirects(
                    client.get(url, follow=True),
                    redirect
                )
