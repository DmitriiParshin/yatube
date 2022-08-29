from django.contrib.auth import get_user_model
from django.db import models

from core.models import CreatedModel

User = get_user_model()


class Post(CreatedModel):
    text = models.TextField('Текст поста', help_text='Введите текст поста')
    author = models.ForeignKey(
        User,
        verbose_name='Автор поста',
        on_delete=models.CASCADE,
        related_name='posts',
    )
    group = models.ForeignKey(
        'Group',
        verbose_name='Группа поста',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        help_text='Выберете группу для поста'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True,
        help_text='Выберете изображение для этого поста'
    )

    class Meta:
        ordering = ('created',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField('Название группы', max_length=200,
                             help_text='Введите название группы')
    slug = models.SlugField('Слаг группы', unique=True)
    description = models.TextField('Описание группы',
                                   help_text='Введите описание группы')

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        verbose_name='Комментарий к посту',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор комментария',
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField('Текст комментария',
                            help_text='Введите текст комментария')

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Подписчик',
        on_delete=models.CASCADE,
        related_name='follower',
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор, на которого подписались',
        on_delete=models.CASCADE,
        related_name='following',
    )
