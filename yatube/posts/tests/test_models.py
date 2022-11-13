from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='auth'),
            text='Текстовый пост',
            group=cls.group,
        )

    def test_models_have_correct_object_names(self):
        self.group = PostModelTest.group
        self.group_str = str(self.group)
        self.assertEqual(
            len(str(PostModelTest.post)),
            14
        )
        self.assertEqual(
            self.group_str,
            self.group.title
        )

    def test_verbose_name(self):
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value
                )

    def test_help_text(self):
        post = PostModelTest.post
        field_help_texts = {
            'text': "Введите текст поста",
            'pub_date': "Укажите дату публикации",
            'author': "Укажите автора поста",
            'group': "Выбор группы",
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value
                )
