from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.constraints import UniqueConstraint

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст публикации',
        help_text='Введите текст публикации',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    author = models.ForeignKey(
        User,
        blank=True,
        null=True,
        # Если из таблицы User будет удалён пользователь, то будут удалены
        # все связанные с ним посты
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор публикации',
    )
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='g_posts',
        verbose_name='Группа публикации',
        help_text='Укажите группу публикации',
    )
    # Поле для картинки (необязательное)
    image = models.ImageField(
        verbose_name='Изображение',
        upload_to='posts/',
        blank=True,
        null=True,
        help_text='Добавьте картинку к публикации',
    )

    class Meta:
        ordering = ['-pub_date', ]

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name='Пост, к которому оставлен комментарий',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    text = models.TextField(
        max_length=1000,
        verbose_name='Текст комментария',
        help_text='Введите текст комментария'
    )
    created = models.DateTimeField(
        verbose_name='Дата публикации комментария',
        help_text='Введите текст комментария',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        ordering = ['-created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text


class Follow(models.Model):
    # кто подписывается
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        blank=True, null=True,
    )
    # на кого подписываются
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        blank=True, null=True,
    )

    class Meta:
        UniqueConstraint(fields=['user', 'author'], name='unique_follower')
