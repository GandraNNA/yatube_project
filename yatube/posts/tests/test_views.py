from http import HTTPStatus

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from .. import models
from ..forms import PostForm
from ..models import Post, Group, User, Follow

INDEX_URL = reverse('posts:index')
CREATE_POST_URL = reverse('posts:create_post')
TEST_SLUG = 'test_slug'
GROUP_LIST_URL = reverse('posts:group_list',
                         kwargs={'slug': TEST_SLUG})


class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.User = models.User
        cls.post_author = cls.User.objects.create_user(
            username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=TEST_SLUG,
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text='Тестовый пост',
            image='small.gif'
        )
        cls.form = PostForm()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cache.clear()

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='Anna')
        self.second_user = User.objects.create_user(username='Alex')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        # self.authorized_client.force_login(self.second_user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post_author)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': INDEX_URL,
            'posts/group_list.html': GROUP_LIST_URL,
            'posts/profile.html': reverse(
                'posts:profile', kwargs={
                    'username': f'{self.user}'}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': f'{self.post.id}'}
            ),
            'posts/create_post.html': CREATE_POST_URL,
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': f'{self.post.id}'}),
            follow=True)
        self.assertTemplateUsed(response, 'posts/post_detail.html')
        response = self.authorized_author.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': f'{self.post.id}'}))
        self.assertTemplateUsed(response, 'posts/create_post.html')

    def test_home_page_show_correct_context(self):
        # Проверка контекста на главной странице
        response = self.authorized_client.get(INDEX_URL)
        first_object = response.context['page_obj'][0]
        image_in_context = response.context['image']
        task_author_0 = first_object.author
        task_text_0 = first_object.text
        self.assertEqual(task_author_0.username, 'author')
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertTrue(image_in_context)

    def test_group_posts_page_show_correct_context(self):
        # Проверка картинки на странице группы
        response = self.authorized_client.get(GROUP_LIST_URL)
        task_group = response.context['group']
        image_in_context = response.context['image']
        self.assertEqual(task_group.title, 'Тестовая группа')
        self.assertTrue(image_in_context)

    def test_profile_show_correct_context(self):
        # Проверка картинки на странице профиля
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': f'{self.user}'}))
        author = response.context['author']
        task_title = response.context['title']
        image_in_context = response.context['image']
        self.assertEqual(task_title, 'Профайл пользователя ')
        self.assertEqual(author.username, self.user.username)
        self.assertTrue(image_in_context)

    def test_post_detail_show_correct_context(self):
        # Проверка картинки на отдельной странице поста
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}
                    )
        )
        first_object = response.context['post']
        image_in_context = response.context['image']
        task_author_0 = first_object.author
        task_text_0 = first_object.text
        self.assertEqual(task_author_0.username, 'author')
        self.assertEqual(task_text_0, 'Тестовый пост')
        self.assertTrue(image_in_context)

    def test_edit_post_show_correct_context(self):
        response = self.authorized_author.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': f'{self.post.id}'}),
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        get_form = response.context['form']
        self.assertIsNotNone(get_form)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = get_form.fields[value]
                self.assertIsInstance(form_field, expected)

    def test_create_post_show_correct_context(self):
        # Проверка контекста и записи в БД при отправке картинки
        # через форму
        response = self.authorized_client.get(CREATE_POST_URL)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        get_form = response.context['form']
        self.assertIsNotNone(get_form)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = get_form.fields[value]
                self.assertIsInstance(form_field, expected)

    def test_cash(self):
        # Проверка кэша на главной странице
        response = self.authorized_client.get(reverse('posts:index'))
        Post.objects.get(pk=self.post.pk).delete()
        second_response = self.authorized_client.get(
            reverse('posts:index'))
        self.assertEqual(response.content, second_response.content)


class TestFollow(TestCase):

    def setUp(self) -> None:
        self.follower_client = Client()
        self.following_client = Client()
        self.follower = User.objects.create_user(username='follower')
        self.following = User.objects.create_user(
            username='following')
        self.follower_client.force_login(self.follower)
        self.following_client.force_login(self.following)
        self.post = Post.objects.create(
            author=self.following,
            text='Тестовый пост',
        )

    def test_new_post_in_followers_feed(self):
        # Новая запись пользователя появляется в ленте тех, кто на
        # него подписан и не появляется в ленте тех, кто не подписан
        self.follower_client.force_login(self.follower)
        self.follower_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': f'{self.following}'})
        )
        self.assertTrue(Follow.objects.filter(
            user=self.follower,
            author=self.following).exists()
                        )

        Follow.objects.create(user=self.follower,
                              author=self.following)
        response = self.follower_client.get('/follow/')
        post_text = response.context['page_obj'][0].text
        self.assertEqual(post_text, 'Тестовый пост')

        response = self.following_client.get('/follow/')
        self.assertNotContains(response, 'Тестовый пост')

    def test_follow_and_unfollow(self):
        # Авторизованный пользователь может подписываться на других
        #  пользователей и удалять их из подписок.
        follows_count = Follow.objects.count()

        self.follower_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': f'{self.following.username}'})
        )
        self.assertEqual(
            Follow.objects.all().count(),
            follows_count + 1
        )

        self.follower_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': f'{self.following.username}'})
        )
        self.assertEqual(Follow.objects.all().count(), follows_count)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        for i in range(13):
            cls.post = Post.objects.create(
                group=cls.group,
                author=cls.post_author,
                text='Тестовый пост',
            )

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_contains_ten_records(self):
        # Страницы index, group_list, profile  содержат 10 записей
        templates = {
            'posts/index.html': INDEX_URL,
            'posts/group_list.html': GROUP_LIST_URL,
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': f'{self.post_author}'}
            ),
        }
        for template, reverse_name in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 settings.NUMBER_OF_POSTS_ON_PAGE)
