from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class CreatedModel(models.Model):
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        db_index=True,
        null=True,
    )
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )

    class Meta:
        abstract = True
        ordering = ('pub_date',)
