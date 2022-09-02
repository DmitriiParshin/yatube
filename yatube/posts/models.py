from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel


User = get_user_model()


class Post(CreatedModel):
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    group = models.ForeignKey(
        'Group',
        verbose_name='Группа поста',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text='Выберете группу для поста'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
        help_text='Выберете изображение для поста'
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
        default_related_name = 'posts'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        max_length=200,
        help_text='Введите название группы'
    )
    slug = models.SlugField(
        'Слаг группы',
        unique=True
    )
    description = models.TextField(
        'Описание группы',
        help_text='Введите описание группы'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        verbose_name='Комментарий к посту',
        on_delete=models.CASCADE
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Введите комментарий'
    )

    class Meta(CreatedModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower'
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор, на которого подписан',
        on_delete=models.CASCADE,
        related_name='following'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(fields=['user', 'author'],
                                    name='already_following')
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
