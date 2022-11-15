from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

POSTS_ON_PAGE = 13
SECOND_PAGE_POSTS = 3

class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='user')
        cls.user_2 = User.objects.create_user(username='user_2')
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
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='slug-for-test-2',
        )
        cls.posts_count = Post.objects.filter(group=cls.group).count()
        cls.post_2 = Post.objects.create(
            text='Тестовый пост автора 2',
            author=cls.user_2,
            group=cls.group_2
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.urls_templates = (
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username]),
            reverse('posts:post_detail', args=[self.post.id]),
            reverse('posts:post_edit', args=[self.post.id]),
        )

    def test_pages_show_correct_context(self):
        """
        Шаблоны страниц index, group_list, profile
        сформированы с правильным контекстом
        """
        for page in self.urls_templates:
            try:
                response = self.authorized_client.get(page)
                self.assertEqual(
                    response.context['page_obj'][0].text,
                    self.post.text
                )
                self.assertEqual(
                    response.context['page_obj'][0].author,
                    self.post.author
                )
                self.assertEqual(
                    response.context['page_obj'][0].group,
                    self.post.group
                )
            except KeyError:
                self.assertEqual(
                    response.context['post'].text,
                    self.post.text
                )
                self.assertEqual(
                    response.context['post'].group.title,
                    self.group.title
                )
                self.assertEqual(
                    response.context['post'].author,
                    self.post.author
                )

    def test_post_correct_created_for_another_user(self):
        """
        Пост при создании не попадает на чужую групп-ленту
        но виден на главной и в группе
        """
        response = self.authorized_client.get(
            self.urls_templates[2]
        )
        group = Post.objects.filter(group=self.group).count()
        profile = response.context['page_obj']
        self.assertNotIn(
            self.post_2,
            profile
        )
        self.assertEqual(
            group,
            self.posts_count
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slug-for-test',
            description='Тестовое описание',
        )
        post_list = []
        for i in range(POSTS_ON_PAGE):
            post_list.append(
                Post(
                    group=cls.group,
                    author=cls.user,
                    text=f'Тестовый текст {i} - го поста'
                )
            )
        Post.objects.bulk_create(post_list)

    def setUp(self) -> None:
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.url_templates = (
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username]),
        )

    def test_correct_the_number_of_posts_on_the_pages_no_auth_users(self):
        """
        Проверка количества постов на первой и второй странице
        для авторизованного и неавторизованного пользователя.
        """
        for page in self.url_templates:
            self.assertEqual(
                len(self.guest_client.get(page).context['page_obj']),
                settings.LIMIT_OF_POSTS
            )
            self.assertEqual(
                len(self.guest_client.get(
                    page + '?page=2'
                ).context['page_obj']),
                SECOND_PAGE_POSTS
            )
            self.assertEqual(
                len(self.authorized_client.get(page).context['page_obj']),
                settings.LIMIT_OF_POSTS
            )
            self.assertEqual(
                len(self.authorized_client.get(
                    page + '?page=2'
                ).context['page_obj']),
                SECOND_PAGE_POSTS
            )
