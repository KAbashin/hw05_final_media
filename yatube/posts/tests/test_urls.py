from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.core.cache import cache
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create_user(
            username='mrnoname',
        )
        cls.test_group = Group.objects.create(
            slug='test_slug',
            title='Тестовая группа',
        )
        cls.post = Post.objects.create(
            author=cls.test_user,
            group=cls.test_group,
            text='Тестовый текст',
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        # случайный пользователь
        self.random_client = User.objects.create_user(username='RandomUser')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.random_client)
        # автор постов
        self.author_client = Client()
        self.author_client.force_login(PostURLTest.test_user)

    # Проверяем общедоступные страницы
    def test_urls_for_guest_client(self):
        """Проверка кодов ответа страниц неавторизованному пользователю."""
        status_codes = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    args=[PostURLTest.test_group.slug]): HTTPStatus.OK,
            reverse('posts:profile',
                    args=[PostURLTest.test_user.username]): HTTPStatus.OK,
            reverse('posts:post_detail',
                    args=[PostURLTest.post.id]): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.FOUND,
            reverse('posts:post_edit',
                    args=[PostURLTest.post.id]): HTTPStatus.FOUND,
            reverse('posts:add_comment',
                    args=[PostURLTest.post.id]): HTTPStatus.FOUND,
            reverse('posts:follow_index'): HTTPStatus.FOUND,
            reverse('posts:profile_follow',
                    args=[PostURLTest.test_user.username]): HTTPStatus.FOUND,
            reverse('posts:profile_unfollow',
                    args=[PostURLTest.test_user.username]): HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for page, status_code in status_codes.items():
            with self.subTest(status_code=status_code):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, status_code)

    # Проверяем доступность страниц для авторизованного пользователя
    def test_urls_for_authorized_client(self):
        """Проверка кодов ответа страниц авторизованному пользователю."""
        status_codes = {
            reverse('posts:index'): HTTPStatus.OK,
            reverse('posts:group_list',
                    args=[PostURLTest.test_group.slug]): HTTPStatus.OK,
            reverse('posts:profile',
                    args=[PostURLTest.test_user.username]): HTTPStatus.OK,
            reverse('posts:post_detail',
                    args=[PostURLTest.post.id]): HTTPStatus.OK,
            reverse('posts:post_create'): HTTPStatus.OK,
            reverse('posts:post_edit',
                    args=[PostURLTest.post.id]): HTTPStatus.OK,
            reverse('posts:add_comment',
                    args=[PostURLTest.post.id]): HTTPStatus.FOUND,
            reverse('posts:follow_index'): HTTPStatus.OK,
            reverse('posts:profile_follow',
                    args=[PostURLTest.test_user.username]): HTTPStatus.FOUND,
            reverse('posts:profile_unfollow',
                    args=[PostURLTest.test_user.username]): HTTPStatus.FOUND,
            '/unexisting_page/': HTTPStatus.NOT_FOUND,
        }
        for page, status_code in status_codes.items():
            with self.subTest(status_code=status_code):
                response = self.author_client.get(page)
                self.assertEqual(response.status_code, status_code)

    # Проверка вызываемых шаблонов для каждого адреса
    def test_urls_use_correct_template(self):
        """URL-адрес использует корректный шаблон."""
        templates_url_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args=[PostURLTest.test_group.slug]):
            'posts/group_list.html',
            reverse('posts:profile',
                    args=[PostURLTest.test_user.username]):
            'posts/profile.html',
            reverse('posts:post_detail', args=[PostURLTest.post.id]):
            'posts/post_detail.html',
            reverse('posts:post_edit', args=[PostURLTest.post.id]):
            'posts/create_post.html',
            reverse('posts:post_create'): 'posts/create_post.html',
        }
        for adress, template in templates_url_names.items():
            with self.subTest(adress=adress):
                response = self.author_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_url_post_edit_exists_at_authorized(self):
        """Страница post_edit для случайного авторизованного
        пользователя (не автора)"""
        response = self.authorized_client.get('/posts/1/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
