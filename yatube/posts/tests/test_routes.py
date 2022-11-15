from django.test import TestCase
from django.urls import resolve, reverse

SLUG_FOR_TEST = 'slug-for-test'
USERNAME_FOR_TEST = 'user'
POST_ID = 1

urls = {
    'posts:index': {
        'reverse': reverse('posts:index'),
        'url': '/'
    },
    'posts:group_list': {
        'reverse': reverse('posts:group_list', args=[SLUG_FOR_TEST]),
        'url': f'/group/{SLUG_FOR_TEST}/'
    },
    'posts:profile': {
        'reverse': reverse('posts:profile', args=[USERNAME_FOR_TEST]),
        'url': f'/profile/{USERNAME_FOR_TEST}/'
    },
    'posts:post_create': {
        'reverse': reverse('posts:post_create'),
        'url': '/create/'
    },
    'posts:post_detail': {
        'reverse': reverse('posts:post_detail', args=[POST_ID]),
        'url': f'/posts/{POST_ID}/'
    },
    'posts:post_edit': {
        'reverse': reverse('posts:post_edit', args=[POST_ID]),
        'url': f'/posts/{POST_ID}/edit/'
    }
}


class RoutesTest(TestCase):

    def test_urls_routes(self):
        """Проверка ожидаемых маршрутов URL"""
        for namespace, key in urls.items():
            with self.subTest(view=namespace, url=key['url']):
                self.assertEqual(
                    resolve(key['url']).view_name,
                    namespace
                )
