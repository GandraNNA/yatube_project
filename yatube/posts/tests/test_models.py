from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Comment, Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.post_author = User.objects.create_user(
            username='author')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.post_author,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            author=cls.post_author,
            post=cls.post
        )

    def test_models_have_correct_object_names(self):
        group = PostModelTest.group
        expected_group_name = group.title
        self.assertEqual(expected_group_name, str(group))
        post = PostModelTest.post
        expected_post_text = self.post.text
        self.assertEqual(expected_post_text, str(post.text))
        comment = PostModelTest.comment
        expected_comment_text = self.comment.text
        self.assertEqual(expected_comment_text, str(comment.text))

    def test_verbose_name(self):
        post = PostModelTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEqual(verbose, 'Текст поста')

    def test_text_help_text(self):
        post = PostModelTest.post
        help_text = post._meta.get_field('text').help_text
        self.assertEqual(help_text, 'Введите текст поста')
