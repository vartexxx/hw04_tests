from django.test import TestCase
from django.urls import reverse

SLUG_FOR_TEST = 'slug-for-test'
USERNAME_FOR_TEST = 'user'
POST_ID = 1

urls = [
    ['/', 'index', None],
    [f'/group/{SLUG_FOR_TEST}/', 'group_list', [SLUG_FOR_TEST]],
    [f'/profile/{USERNAME_FOR_TEST}/', 'profile', [USERNAME_FOR_TEST]],
    ['/create/', 'post_create', None],
    [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
    [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
]


class RoutesTest(TestCase):

    def test_urls_routes(self):
        """Проверка ожидаемых маршрутов URL"""
        for url, route, args in urls:
            self.assertEqual(
                url,
                reverse((f'posts:{route}'), args=args)
            )
