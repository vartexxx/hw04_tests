from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

POSTS_ON_PAGES = 55
POSTS_ON_PAGE = 10
POSTS_ON_LAST_PAGE = POSTS_ON_PAGES % 10
num_of_page = f'?page={POSTS_ON_PAGES // POSTS_ON_PAGE + 1}'


USERNAME = 'user'
TEST_USER = 'test_user'
SLUG_1 = 'slug-one'
SLUG_2 = 'slug-two'
SLUG_TEST = 'slug-test'

INDEX_URL = reverse('posts:index')
GROUP_LIST_URL_1 = reverse('posts:group_list', args=[SLUG_1])
GROUP_LIST_URL_2 = reverse('posts:group_list', args=[SLUG_2])
GROUP_LIST_URL_3 = reverse('posts:group_list', args=[SLUG_TEST])
PROFILE_URL = reverse('posts:profile', args=[USERNAME])


class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа 1',
            slug=SLUG_1,
            description='Тестовое описание 1',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug=SLUG_2,
            description='Тестовое описание 2',
        )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group,
        )

    def test_pages_show_correct_context(self):
        """
        Шаблоны страниц index, group_list, profile
        сформированы с правильным контекстом.
        """
        urls = [
            [INDEX_URL, self.authorized_client.get(INDEX_URL)],
            [GROUP_LIST_URL_1, self.authorized_client.get(GROUP_LIST_URL_1)],
            [PROFILE_URL, self.authorized_client.get(PROFILE_URL)],
        ]
        for url, client in urls:
            with self.subTest(url=url):
                self.assertEqual(
                    client.context['page_obj'][0].text,
                    self.post.text
                )
                self.assertEqual(
                    client.context['page_obj'][0].author,
                    self.post.author
                )
                self.assertEqual(
                    client.context['page_obj'][0].group,
                    self.post.group
                )

    def test_posts_group_context_group_list(self):
        """Группа в контексте групп-ленты без искажения атрибутов."""
        self.assertEqual(
            self.authorized_client.get(GROUP_LIST_URL_1).context.get('group'),
            self.group
        )

    def test_post_not_in_another_group(self):
        """Пост не попал на чужую групп-ленту."""
        self.assertNotIn(
            self.post,
            self.authorized_client.get(GROUP_LIST_URL_2).context.get(
                'page_obj'
            )
        )

    def test_posts_page_author_in_context_profile(self):
        """Проверка наличия автора в контексте профиля."""
        self.assertEqual(
            self.user,
            self.authorized_client.get(PROFILE_URL).context.get('author')
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()

        cls.user = User.objects.create_user(username=USERNAME)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG_TEST,
            description='Тестовое описание',
        )
        post_list = [
            Post(
                author=cls.user,
                text=f'Тестовый текст {i}-го поста',
                group=cls.group
            ) for i in range(POSTS_ON_PAGES)
        ]
        Post.objects.bulk_create(post_list)

    def setUp(self) -> None:
        self.guest_client = Client()

    def test_correct_the_number_of_posts_on_the_pages(self):
        """Проверка количества постов на странице первой и последней."""
        urls = [
            [INDEX_URL, POSTS_ON_PAGE],
            [INDEX_URL + num_of_page, POSTS_ON_LAST_PAGE],
            [GROUP_LIST_URL_3, POSTS_ON_PAGE],
            [GROUP_LIST_URL_3 + num_of_page, POSTS_ON_LAST_PAGE],
            [PROFILE_URL, POSTS_ON_PAGE],
            [PROFILE_URL + num_of_page, POSTS_ON_LAST_PAGE],
        ]
        for page, posts in urls:
            self.assertEqual(
                len(self.guest_client.get(page).context['page_obj']),
                posts
            )
