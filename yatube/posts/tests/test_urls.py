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

OK = 200
FOUND = 302
NOT_FOUND = 404


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
        self.guest = Client()
        self.another = Client()
        self.another.force_login(self.user)
        self.author = Client()
        self.author.force_login(self.user_author)

        self.redirect_urls = [
            [
                POST_CREATE_URL,
                self.guest,
                f'{LOGIN}?next={POST_CREATE_URL}'
            ],
            [
                self.POST_EDIT_URL,
                self.guest,
                f'{LOGIN}?next={self.POST_EDIT_URL}'
            ],
            [
                self.POST_EDIT_URL,
                self.another,
                self.POST_DETAIL_URL
            ],
        ]

        self.urls_for_template = [
            ['posts/index.html', INDEX_URL],
            ['posts/group_list.html', GROUP_LIST_URL],
            ['posts/profile.html', PROFILE_URL],
            ['posts/create_post.html', POST_CREATE_URL],
            ['posts/post_detail.html', self.POST_DETAIL_URL],
            ['posts/create_post.html', self.POST_EDIT_URL],
        ]

    def test_posts_urls_correct_status_code(self):
        """
        Проверка доступа к URL различного уровня
        авторизации пользователей.
        """
        urls = [
            [INDEX_URL, self.guest, OK],
            [GROUP_LIST_URL, self.guest, OK],
            [PROFILE_URL, self.guest, OK],
            [self.POST_DETAIL_URL, self.guest, OK],
            [NON_EXISTING_PAGE_URL, self.guest, NOT_FOUND],
            [POST_CREATE_URL, self.guest, FOUND],
            [self.POST_EDIT_URL, self.guest, FOUND],
            [self.POST_EDIT_URL, self.author, OK],
            [self.POST_EDIT_URL, self.another, FOUND],
            [POST_CREATE_URL, self.another, OK],
        ]
        for url, client, status in urls:
            with self.subTest(url=url, client=client):
                self.assertEqual(
                    client.get(url).status_code,
                    status
                )

    def test_posts_urls_correct_redirect(self):
        """Проверка редиректов со страниц."""
        for url, client, redirect in self.redirect_urls:
            with self.subTest(url=url, client=client):
                self.assertRedirects(
                    client.get(url, follow=True),
                    redirect
                )

    def test_posts_urls_uses_correct_templates(self):
        """Проверка использования URL корректных шаблонов."""
        for template, url in self.urls_for_template:
            with self.subTest(url=url):
                self.assertTemplateUsed(
                    self.author.get(url),
                    template
                )
