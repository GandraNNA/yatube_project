from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..forms import PostForm
from ..models import Post, Group

User = get_user_model()


class PagesTests(TestCase):
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

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='HasNoName')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post_author)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={
                    'slug': 'test_slug'}
            ),
            'posts/profile.html': reverse(
                'posts:profile', kwargs={
                    'username': f'{self.user}'}
            ),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={
                    'post_id': f'{self.post.id}'}
            ),
            'posts/create_post.html': reverse('posts:create_post'),

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
         # TODO: Добавить проверку передачи image через context поста
         # на главную страницу.
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        task_author_0 = first_object.author
        task_text_0 = first_object.text
        self.assertEqual(task_author_0.username, 'author')
        self.assertEqual(task_text_0, 'Тестовый пост')

        # context = response.context['post'].image
        # print(context)
        # self.assertEqual(context, 'posts/small.gif')

    def test_group_posts_page_show_correct_context(self):
        """ Добавить проверку картинки на странице группы """
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': 'test_slug'}))
        task_group = response.context['group']
        self.assertEqual(task_group.title, 'Тестовая группа')

    def test_profile_show_correct_context(self):
        """ TODO: Добавить проверку картинки на страницу профиля """
        response = self.authorized_client.get(reverse(
            'posts:profile', kwargs={'username': f'{self.user}'}))
        author = response.context['author']
        task_title = response.context['title']
        self.assertEqual(task_title, 'Профайл пользователя ')
        self.assertEqual(author.username, self.user.username)
        # self.assertTrue(Post.objects.filter(image='posts/'))
        number_of_posts = response.context['number_of_posts']
        self.assertEqual(number_of_posts, 1)

    def test_post_detail_show_correct_context(self):
        """ TODO: Добавить проверку картинки на отдельной странице поста """
        response = self.authorized_client.get(
            reverse('posts:post_detail',
                    kwargs={'post_id': f'{self.post.id}'}
                    )
        )
        first_object = response.context['post']
        task_author_0 = first_object.author
        task_text_0 = first_object.text
        self.assertEqual(task_author_0.username, 'author')
        self.assertEqual(task_text_0, 'Тестовый пост')

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
        response = self.authorized_client.get(
            reverse('posts:create_post'))
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
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': 'test_slug'}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': f'{self.post_author}'}
            ),
        }
        for template, reverse_name in templates.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(len(response.context['page_obj']),
                                 10)
