# post/tests/test_views.py
import tempfile
import shutil

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache

from ..forms import PostForm
from ..models import Group, Post, User, Comment

User = get_user_model()
ITEMS_PER_PAGE = 10
ITEMS_PER_PAGE_3 = 3
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(
            username='test_user',
            password='1234567'
        )
        cls.random_user = User.objects.create_user(
            username='randomuser',
            password='1234567'
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        cls.new_group = Group.objects.create(
            title='Тестовый заголовок 1',
            slug='test_slug_1',
            description='Тестовый текст 1',
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00'
            b'\x05\x04\x04\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00'
            b'\x01\x00\x00\x02\x02\x44\x01\x00\x3b')
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            group=cls.group,
            text='Тестовый заголовок',
            pub_date='04.04.2022',
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            text='Комментарий',
            author=cls.author,
        )

        cls.guest_client = Client()
        cls.authorized_client_author = Client()
        cls.authorized_client_author.force_login(cls.author)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.random_user)

        cls.post_args = {
            'username': cls.random_user.username,
            'post_id': cls.post.id,
        }

    def setUp(self):
        cache.clear()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(settings.MEDIA_ROOT, ignore_errors=True)
        super().tearDownClass()

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_templates(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}):
                'posts/group_list.html',
            reverse('posts:profile', kwargs={'username': self.author}):
                'posts/profile.html',
            reverse('posts:post_detail', kwargs={'post_id': 1}):
                'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:post_edit', kwargs={'post_id': 1}):
                'posts/create_post.html',
        }
        # Проверяем, что при обращении к name вызывается правильный HTML-шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client_author.get(reverse_name)
                self.assertTemplateUsed(response, template)

    # Проверка словаря контекста главной страницы
    def test_post_index_page_show_correct_context(self):
        """Шаблон главной страницы сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.author: first_object.author,
            self.post.text: first_object.text,
            self.group: first_object.group,
            self.post.id: first_object.id,
            self.post.image: first_object.image
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    # Проверка словаря контекста страницы группы
    def test_post_posts_groups_page_show_correct_context(self):
        """Проверяем Context страницы group_posts"""
        response = self.authorized_client_author.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        post_image = response.context['page_obj'][0].image
        first_object = response.context['group']
        context_objects = PostViewsTest.group
        self.assertEqual(first_object, context_objects)
        self.assertEqual(post_image, self.post.image)

    # Проверка словаря контекста страницы пользователя
    def test_post_profile_page_show_correct_context(self):
        """Шаблон страницы пользователя сформирован с правильным контекстом."""
        profile_url = reverse('posts:profile',
                              kwargs={'username': self.author.username})
        response = self.authorized_client_author.get(profile_url)
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.author: first_object.author,
            self.post.text: first_object.text,
            self.group: first_object.group,
            self.post.id: first_object.id,
            self.post.image: first_object.image,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    # Проверка словаря контекста страницы публикации
    def test_post_page_show_correct_context(self):
        """Шаблон страницы публикации сформирован с правильным контекстом."""
        post_url = reverse('posts:post_detail', kwargs={'post_id': 1})
        response = self.authorized_client_author.get(post_url)
        first_object = response.context['post']
        context_objects = {
            self.author: first_object.author,
            self.post.text: first_object.text,
            self.group: first_object.group,
            self.post.id: first_object.id,
            self.post.image: first_object.image,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_post_edit_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:post_edit', kwargs={'post_id': '1'})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertIsInstance(response.context.get('form'), PostForm)
        self.assertTrue('is_edit' in response.context)

    def test_create_page_show_correct_context(self):
        """Шаблон post_create сформирован с правильным контекстом."""
        response = self.authorized_client_author.get(
            reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
        self.assertIsInstance(response.context.get('form'), PostForm)

    def test_post_new_create_appears_on_correct_pages(self):
        """При создании поста он должен появляется на главной странице,
        на странице выбранной группы и в профиле пользователя"""
        exp_pages = [
            reverse('posts:index'),
            reverse(
                'posts:group_list', kwargs={'slug': self.group.slug}),
            reverse(
                'posts:profile', kwargs={'username': self.author.username})
        ]
        for revers in exp_pages:
            with self.subTest(revers=revers):
                response = self.authorized_client_author.get(revers)
                self.assertIn(self.post, response.context['page_obj'])

    def test_posts_not_contain_in_wrong_group(self):
        """При создании поста он не появляется в другой группе"""
        post = Post.objects.get(pk=1)
        response = self.authorized_client_author.get(
            reverse('posts:group_list', kwargs={'slug': self.new_group.slug})
        )
        self.assertNotIn(post, response.context['page_obj'].object_list)

    def test_post_edit_random_user(self):
        """ проверка страницы редактирования поста  авторизованным
        пользователем (не автором)"""
        response_1 = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response_1.status_code, 302)
        post_url = reverse('posts:post_detail',
                           kwargs={'post_id': self.post.id})
        response = self.authorized_client.get(post_url)
        first_object = response.context['post']
        context_objects = {
            self.author: first_object.author,
            self.post.text: first_object.text,
            self.group: first_object.group,
            self.post.id: first_object.id,
            self.post.image: first_object.image,
        }
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_only_authorized_user_add_comment(self):
        """Только авторизованный пользователь может добавлять
        комментарии."""
        comments_count = Comment.objects.count()
        response = reverse('posts:add_comment',
                           kwargs={'post_id': self.post.id})
        form_data = {'text': 'Комментарий'}
        self.guest_client.post(response, form_data)
        self.assertEqual(Comment.objects.count(), comments_count)
        self.authorized_client.post(response, form_data)
        self.assertEqual(Comment.objects.count(), comments_count + 1)

    def test_guest_user_add_comment(self):
        """Не авторизованный пользователь не может добавлять
        комментарии."""
        comments_count = Comment.objects.count()
        comments = {
            'text': 'Комментарий',
            'author': self.author,
            'post': self.post,
        }
        self.guest_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.pk}),
            data=comments,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertFalse(Post.objects.filter(text='Комментарий', ).exists())

    def test_cache_on_index_page_works_correct(self):
        """Кэширование данных на главной странице работает корректно."""
        response = self.authorized_client.get(reverse('posts:index'))
        cached_content = response.content
        Post.objects.all().delete()
        response = self.authorized_client.get(reverse('posts:index'))
        cached_content_after_delete = response.content
        self.assertEqual(
            cached_content,
            cached_content_after_delete,
            'Кэширование работает некорректно.'
        )
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(
            cached_content,
            response.content,
            'Кэширование после очистки работает некорректно'
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый текст',
        )
        # bulk_create для создания
        # 13 объектов модели Post
        objs = [
            Post(
                author=cls.author,
                group=cls.group,
                text='Тестовый заголовок',
                pub_date='22.02.2022',
            )
            for bulk in range(1, 14)
        ]
        cls.post = Post.objects.bulk_create(objs)

    def setUp(self):
        cache.clear()

    def test_first_page_contains_ten_records(self):
        """Проверка: на первой странице должно быть 10 постов."""
        response = self.client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), ITEMS_PER_PAGE)

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста."""
        response = self.client.get(reverse('posts:index') + '?page=2')
        self.assertEqual(len(response.context['page_obj']), ITEMS_PER_PAGE_3)

    def test_group_list_contains_ten_pages(self):
        """Проверка: на  странице group_list должно быть 10 постов."""
        response = self.client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        )
        self.assertEqual(len(response.context['page_obj']), ITEMS_PER_PAGE)

    def test_profile_contains_ten_records(self):
        """Проверка: на  странице профиля должно быть 10 постов."""
        response = self.client.get(reverse(
            'posts:profile', kwargs={'username': self.author.username}))
        self.assertEqual(len(response.context['page_obj']), ITEMS_PER_PAGE)
