from django.contrib import admin
from .models import Group, Post, Comment, Follow


class PostAdmin(admin.ModelAdmin):
    # Это позволит изменять поле group в любом посте без лишних движений
    # мышкой, прямо из списка постов
    list_editable = ("group",)
    # Перечисляем поля, которые должны отображаться в админке
    list_display = (
        'pk',
        'text',
        'pub_date',
        'author',
        'group'
    )
    # поля ссылки на пост
    list_display_links = ('pk', 'text',)
    # Добавляем интерфейс для поиска по тексту постов
    search_fields = ('text',)
    # Добавляем возможность фильтрации по дате
    list_filter = ('pub_date',)
    # Это свойство сработает для всех колонок: где пусто — там будет
    # эта строка
    empty_value_display = '-пусто-'


class GroupAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'title',
        'slug'
        'description',
    )
    search_fields = ('text',)
    list_filter = ('title',)
    empty_value_display = '-пусто-'


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'author',
        'text',
        'created',
        'post',
    )


class FollowAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author',
    )


admin.site.register(Post, PostAdmin)
admin.site.register(Group)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Follow, FollowAdmin)
