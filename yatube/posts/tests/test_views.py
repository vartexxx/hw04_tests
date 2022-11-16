from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

POSTS_ON_PAGES = 60

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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.id])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.id])

    def setUp(self) -> None:
        self.another = Client()
        self.another.force_login(self.user)

    def test_pages_show_correct_context(self):
        """
        Шаблоны страниц index, group_list, profile, post_detail, post_edit
        сформированы с правильным контекстом.
        """
        urls = [
            [INDEX_URL, self.another.get(INDEX_URL)],
            [GROUP_LIST_URL_1, self.another.get(GROUP_LIST_URL_1)],
            [PROFILE_URL, self.another.get(PROFILE_URL)],
            [self.POST_DETAIL_URL, self.another.get(self.POST_DETAIL_URL)],
            [self.POST_EDIT_URL, self.another.get(self.POST_EDIT_URL)],
        ]
        for url, client in urls:
            with self.subTest(url=url):
                try:
                    post = client.context['page_obj'][0]
                    self.assertEqual(
                        client.context.get("page_obj").object_list[0],
                        post
                    )
                    self.assertEqual(
                        post.text,
                        self.post.text
                    )
                    self.assertEqual(
                        post.author,
                        self.post.author
                    )
                    self.assertEqual(
                        post.group,
                        self.post.group
                    )
                except KeyError:
                    post = client.context['post']
                    self.assertEqual(
                        post.text,
                        self.post.text
                    )
                    self.assertEqual(
                        post.group.id,
                        self.group.id
                    )
                    self.assertEqual(
                        post.author,
                        self.user
                    )

    def test_posts_group_context_group_list(self):
        """Группа в контексте групп-ленты без искажения атрибутов."""
        group = self.another.get(GROUP_LIST_URL_1).context.get('group')
        self.assertEqual(group, self.group)
        self.assertEqual(group.title, self.group.title)
        self.assertEqual(group.slug, self.group.slug)
        self.assertEqual(group.description, self.group.description)

    def test_post_not_in_another_group(self):
        """Пост не попал на чужую групп-ленту."""
        self.assertNotIn(
            self.post,
            self.another.get(GROUP_LIST_URL_2).context.get(
                'page_obj'
            )
        )

    def test_posts_page_author_in_context_profile(self):
        """Проверка наличия автора в контексте профиля."""
        self.assertEqual(
            self.user,
            self.another.get(PROFILE_URL).context.get('author')
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUp(self) -> None:
        self.user = User.objects.create_user(username=USERNAME)
        self.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG_TEST,
            description='Тестовое описание',
        )
        Post.objects.bulk_create([
            Post(
                author=self.user,
                text=f'Тестовый текст {i}-го поста',
                group=self.group
            ) for i in range(POSTS_ON_PAGES)
        ])
        self.guest = Client()

    def test_correct_the_number_of_posts_on_the_pages(self):
        """Проверка количества постов на странице первой и последней."""
        NUM_OF_PAGE = f'?page={POSTS_ON_PAGES // settings.LIMIT_OF_POSTS + 1}'
        POSTS_ON_LAST_PAGE = POSTS_ON_PAGES % 10
        if POSTS_ON_PAGES % 10 == 0:
            NUM_OF_PAGE = f'?page={POSTS_ON_PAGES // settings.LIMIT_OF_POSTS}'
            POSTS_ON_LAST_PAGE = settings.LIMIT_OF_POSTS
        urls = [
            [INDEX_URL, settings.LIMIT_OF_POSTS],
            [INDEX_URL + NUM_OF_PAGE, POSTS_ON_LAST_PAGE],
            [GROUP_LIST_URL_3, settings.LIMIT_OF_POSTS],
            [GROUP_LIST_URL_3 + NUM_OF_PAGE, POSTS_ON_LAST_PAGE],
            [PROFILE_URL, settings.LIMIT_OF_POSTS],
            [PROFILE_URL + NUM_OF_PAGE, POSTS_ON_LAST_PAGE],
        ]
        for page, posts in urls:
            self.assertEqual(
                len(self.guest.get(page).context['page_obj']),
                posts
            )
