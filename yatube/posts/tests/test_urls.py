from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text='Тестовый пост',
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_for_everyone(self):
        """ Страницы: '/';'/group/<slug>/';'/profile/<str:username>/';
        '/posts/<int:post_id>/' доступны любому пользователю."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_is_edit_page(self):
        """Страница 'posts/<int:post_id>/edit/' доступна автору"""
        url = f'/posts/{self.post.id}/edit/'
        client = Client()
        client.force_login(self.post_author)
        response = client.get(url)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_page(self):
        """Страница 'create/' доступна авторизованному пользователю"""
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_404_page(self):
        """Запрос к несуществующей странице вернёт ошибку 404"""
        response = self.guest_client.get('/n0t_ex15ting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
