from http import HTTPStatus

from django.test import TestCase, Client
from django.urls import reverse

from ..models import Post, Group, User


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

        self.urls_templates = (
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user_author.username]),
            reverse('posts:post_detail', args=[self.post.id]),
            reverse('posts:post_edit', args=[self.post.id]),
            reverse('posts:post_create'),
            '/non_existing_page/',
        )
        self.urls_redirect = {
            '/posts/' + str(self.post.id) + '/edit/':
                '/auth/login/?next=/posts/' + str(self.post.id) + '/edit/',
            '/create/':
                '/auth/login/?next=/create/',
        }
        self.urls_routes = {
            '/': 'posts/index.html',
            '/group/' + str(self.group.slug) + '/': 'posts/group_list.html',
            '/profile/' + str(self.user.username) + '/': 'posts/profile.html',
            '/create/': 'posts/create_post.html',
            '/posts/' + str(self.post.id) + '/edit/': 'posts/create_post.html',
            '/posts/' + str(self.post.id) + '/': 'posts/post_detail.html',
        }

    def test_posts_urls_exists_at_desired_location_any_types_of_users(self):
        """
        Проверка доступа к URL различного уровня
        авторизации пользователей.
        """
        for page in self.urls_templates:
            try:
                try:
                    try:
                        self.assertEqual(
                            self.guest_client.get(page).status_code,
                            HTTPStatus.OK
                        )
                    except AssertionError:
                        self.assertEqual(
                            self.authorized_client.get(page).status_code,
                            HTTPStatus.OK
                        )
                except AssertionError:
                    self.assertEqual(
                        self.author_client.get(page).status_code,
                        HTTPStatus.OK
                    )
            except AssertionError:
                self.assertEqual(
                    self.guest_client.get(page).status_code,
                    HTTPStatus.NOT_FOUND
                )
                self.assertEqual(
                    self.authorized_client.get(page).status_code,
                    HTTPStatus.NOT_FOUND
                )
                self.assertEqual(
                    self.author_client.get(page).status_code,
                    HTTPStatus.NOT_FOUND
                )

    def test_posts_urls_redirect(self):
        """Проверка редиректов для пользователей типа - гость."""
        for url, redirect_page in self.urls_redirect.items():
            with self.subTest(redirect_page=redirect_page):
                self.assertRedirects(
                    self.guest_client.get(url, follow=True),
                    redirect_page
                )

    def test_posts_urls_uses_correct_template(self):
        """URL - адрес приложения Posts использует соответствующий шаблон."""
        for url, template in self.urls_routes.items():
            with self.subTest(template=template):
                try:
                    self.assertTemplateUsed(
                        self.authorized_client.get(url),
                        template
                    )
                except AssertionError:
                    self.assertTemplateUsed(
                        self.author_client.get(url),
                        template
                    )
