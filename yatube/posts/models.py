from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel
from django.db.models import UniqueConstraint

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        max_length=200
    )
    slug = models.SlugField(
        'Идентификатор группы',
        max_length=200,
        unique=True
    )
    description = models.TextField('Описание')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='order_group_posts',
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )


class Meta:
    ordering = ('pub_date',)
    verbose_name = 'Пост'
    verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        'Комментарий',
        help_text='Введите текст комментария'
    )

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following'
    )

    def __str__(self):
        return self.author

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=~models.Q(
                    user=models.F('author')),
                name='self-subscription_not_allowed'),
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_users'
            ),
        ]
