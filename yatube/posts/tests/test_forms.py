from http import HTTPStatus
from django.contrib.auth import get_user_model

from ..forms import PostForm
from ..models import Group, Post

from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class TaskCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаём тестовую запись в БД
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
        cls.form = PostForm()

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.post_author)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:create_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, (reverse(
            'posts:profile',
            kwargs={'username': f'{self.post_author}'})))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост',
                author=self.post_author,
                group=self.group.id
            ).exists()
        )

    def test_edit_post(self):
        form_data = {
            'text': 'Тестовый пост',
            'group': self.group.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit',
                    kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, (reverse(
            'posts:post_detail',
            kwargs={'post_id': f'{self.post.id}'})))
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый пост',
                author=self.post_author,
                group=self.group.id
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
