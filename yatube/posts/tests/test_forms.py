import shutil
import tempfile
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..forms import PostForm
from ..models import Group, Post, User
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='noname')
        cls.group = Group.objects.create(
            title='Тестовый Заголовок',
            slug='test_slug',
            description='Тестовое описание группы'
        )
        cls.group_new = Group.objects.create(
            title='Тестовый Заголовок new',
            slug='test_slug_new',
            description='Тестовое описание группы new'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Проверка формы создания поста"""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'author': self.user,
            'image': uploaded,
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertRedirects(
            response, reverse(
                'posts:profile',
                kwargs={'username': f'{self.user}'}
            ))
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=self.group.id,
            image='posts/small.gif',
        ).first())

    def test_upload_not_image(self):
        """Проверка формы создания поста с загрузкой не поддерживаемого
        файла. Текст ошибки получаем из response.context.get('form').errors """
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded_wrong_ext = SimpleUploadedFile(
            name='small.txt',
            content=small_gif,
            content_type='image/gif'
        )
        form_data_1 = {
            'author': self.user,
            'image': uploaded_wrong_ext,
            'text': 'Тестовый текст',
            'group': self.group.id,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data_1,
            follow=True
        )
        error_mg = ("Формат файлов 'txt' не поддерживается. Поддерживаемые "
                    "форматы файлов: 'bmp, dib, gif, tif, tiff, jfif, jpe, jpg"
                    ", jpeg, pbm, pgm, ppm, pnm, png, apng, blp, bufr, cur, "
                    "pcx, dcx, dds, ps, eps, fit, fits, fli, flc, ftc, ftu, "
                    "gbr, grib, h5, hdf, jp2, j2k, jpc, jpf, jpx, j2c, icns, "
                    "ico, im, iim, mpg, mpeg, mpo, msp, palm, pcd, pdf, pxr, "
                    "psd, bw, rgb, rgba, sgi, ras, tga, icb, vda, vst, webp, "
                    "wmf, emf, xbm, xpm'.")
        self.assertFormError(
            response,
            'form',
            'image',
            error_mg
        )

    def test_edit_post(self):
        """Проверка формы редактирования поста"""
        form_data = {
            'text': 'Тестовый текст new',
            'group': PostFormTest.group_new.id,
            'author': self.user
        }
        response = self.authorized_client.post(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': f'{self.post.id}'}),
            data=form_data,
            follow=True
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertRedirects(
            response,
            reverse(
                'posts:post_detail',
                kwargs={'post_id': f'{self.post.id}'}
            ))
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст new',
                group=PostFormTest.group_new.id,
                author=self.user
            ).exists())
        self.assertFalse(
            Post.objects.filter(
                text='Тестовый текст',
                group=PostFormTest.group.id
            ).exists())

    def test_guest_client_could_not_create_posts(self):
        """Проверка невозможности создания поста неавторизованным
        пользователем."""
        posts_before = Post.objects.count()
        form_data = {
            'group': self.group.id,
            'text': 'Тестовый текст',
            'author': self.guest_client,
        }
        response = self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        expected_redirect = str(reverse('users:login') + '?next='
                                + reverse('posts:post_create'))
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(Post.objects.count(), posts_before)


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(
            username='test_username',
            email='testmail@gmail.com',
            password='Qwerty123',
        )
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.test_user)
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.test_user,
            group=cls.group,
            text='Тестовый текст',
        )

    def test_authorized_client_can_create_comments(self):
        """Авторизованный пользователь может комментировать посты."""
        comments_before = self.post.comments.count()
        form_data = {
            'text': 'Тестовый комментарий к посту',
        }
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id, }),
            data=form_data,
            follow=True,
        )
        self.assertEqual(self.post.comments.count(), comments_before + 1)
        last_comment = self.post.comments.last()
        self.assertEqual(last_comment.text, form_data['text'])

    def test_guest_client_could_not_create_comments(self):
        """Неавторизованный пользователь не может комментировать посты."""
        comments_before = self.post.comments.count()
        form_data = {
            'text': 'Тестовый комментарий к посту',
        }
        response = self.guest_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id, }),
            data=form_data,
            follow=True,
        )
        expected_redirect = str(reverse('users:login') + '?next='
                                + reverse('posts:add_comment',
                                          kwargs={'post_id': self.post.id, }))
        self.assertRedirects(response, expected_redirect)
        self.assertEqual(self.post.comments.count(), comments_before)
