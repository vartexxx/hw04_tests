from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostViewsTest(TestCase):
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

    def test_posts_pages_uses_correct_template(self):
        """URL - адрес приложения Posts использует соответствующий шаблон."""
        templates_pages_names = {
            'posts/index.html': reverse(
                'posts:index'
            ),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': self.user}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ),
            'posts/create_post.html': reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ),
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_oject = response.context['page_obj'][0]
        index_text = first_oject.text
        index_group = first_oject.group.title
        index_author = first_oject.author.username
        self.assertEqual(index_text, 'Тестовый пост')
        self.assertEqual(index_group, 'Тестовая группа')
        self.assertEqual(index_author, 'user')

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'slug-for-test'})
        )
        for post in response.context['page_obj']:
            group_list_author = post.author.username
            group_list_text = post.text
            group_list_group = post.group.title
            self.assertEqual(group_list_author, 'user')
            self.assertEqual(group_list_text, 'Тестовый пост')
            self.assertEqual(group_list_group, 'Тестовая группа')

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'user'})
        )
        for post in response.context['page_obj']:
            profile_author = post.author.username
            profile_text = post.text
            profile_group = post.group.title
            self.assertEqual(profile_author, 'user')
            self.assertEqual(profile_text, 'Тестовый пост')
            self.assertEqual(profile_group, 'Тестовая группа')

    def test_post_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        test_post_detail_id = 1
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': test_post_detail_id}
            )
        )
        self.assertEqual(
            response.context.get('post').text,
            'Тестовый пост'
        )
        self.assertEqual(
            response.context.get('post').group.title,
            'Тестовая группа'
        )
        self.assertEqual(
            response.context.get('post').author.username,
            'user'
        )

    def test_edit_post_page_show_correct_context(self):
        """
        Шаблон create_post при редактировании поста сформирован
        с правильным контекстом.
        """
        test_post_create_id = 1
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': test_post_create_id}
            )
        )
        self.assertEqual(
            response.context.get('post').text,
            'Тестовый пост'
        )
        self.assertEqual(
            response.context.get('post').group.title,
            'Тестовая группа'
        )

    def test_create_post_page_show_correct_context(self):
        """
        Шаблон create_post при создании поста сформирован
        с правильным контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:post_create'
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)


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
        for i in range(settings.MIN_POSTS, settings.MAX_POSTS):
            cls.post = Post.objects.create(
                author=cls.user,
                group=cls.group,
                text=f'Текст {i} - го поста',
            )

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_first_page_of_index_contains_ten_records(self):
        """Количество постов на первой странице шаблона index равно 10"""
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(
            len(response.context['page_obj']),
            settings.LIMIT_OF_POSTS
        )

    def test_second_page_of_index_contains_three_records(self):
        """Количество постов на второй странцие шаблона index равно 3"""
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            settings.SECOND_PAGE_POSTS
        )

    def test_first_page_of_group_list_contains_ten_records(self):
        """Количество постов на первой странице шаблона group_list"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug}
            )
        )
        self.assertEqual(
            len(response.context['page_obj']),
            settings.LIMIT_OF_POSTS
        )

    def test_second_page_of_group_list_contains_three_records(self):
        """Количество постов на второй странице шаблона group_list"""
        response = self.authorized_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}
            ) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            settings.SECOND_PAGE_POSTS
        )

    def test_first_page_of_profile_conatins_ten_records(self):
        """Количество постов на первой странице шаблона profile"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            )
        )
        self.assertEqual(
            len(response.context['page_obj']),
            settings.LIMIT_OF_POSTS
        )

    def test_second_page_of_profile_contains_three_records(self):
        """Количество постов на второй странице шалона profile"""
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username}
            ) + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            settings.SECOND_PAGE_POSTS
        )
