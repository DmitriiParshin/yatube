import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Comment, Group, Post


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    def setUp(self):
        self.test_image = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.image = SimpleUploadedFile(
            name='test_image.gif',
            content=self.test_image,
            content_type='image/gif'
        )
        self.user = User.objects.create_user(username='test_user')
        self.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test_slug',
            description='Описание тестовой группы',
        )
        self.post = Post.objects.create(
            author=User.objects.create_user(username='test_author'),
            text='Текст тестового поста',
            group=self.group
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_anonymous(self):
        """Проверка создания поста неавторизованным пользователем."""
        form_data = {
            'text': self.post.text,
            'group': self.group.id,
            'image': self.image,
        }
        posts_count = Post.objects.count()
        response = self.client.post(reverse('posts:post_create'),
                                    data=form_data,
                                    follow=True,
                                    )
        self.assertRedirects(response, reverse('users:login')
                             + '?next=/create/')
        self.assertEqual(Post.objects.count(), posts_count)

    def test_create_post(self):
        """Проверка создания поста."""
        self.post.delete()
        post_count = Post.objects.count()
        form_data = {
            'text': 'Текст для создания нового поста',
            'group': self.group.id,
            'image': self.image,
        }
        response = self.authorized_client.post(reverse('posts:post_create'),
                                               data=form_data,
                                               follow=True
                                               )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=(self.user.username,))
        )
        post = Post.objects.first()
        self.assertEqual(post_count, 0)
        self.assertEqual(Post.objects.count(), 1)
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.image, 'posts/test_image.gif')

    def test_edit_post(self):
        """Проверка редактирования поста."""
        post_count = Post.objects.count()
        self.assertEqual(post_count, 1)
        new_group = Group.objects.create(
            title='Название новой тестовой группы',
            slug='new_test_slug',
            description='Описание новой тестовой группы',
        )
        image = SimpleUploadedFile(
            name='new_test_image.gif',
            content=self.test_image,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Измененный текст',
            'group': new_group.id,
            'image': image,
        }
        response = self.authorized_author.post(
            reverse('posts:post_edit', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('posts:post_detail',
                                               args=(self.post.id,))
                             )
        self.assertEqual(Post.objects.count(), post_count)
        post = Post.objects.first()
        self.assertEqual(post.author, self.post.author)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image, 'posts/new_test_image.gif')
        response = self.authorized_author.get(
            reverse('posts:group_list', args=(self.group.slug,)))
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(post_count, Post.objects.count())

    def test_create_comment_anonymous(self):
        """Проверка создания комментария неавторизованным пользователем."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        reverse_on_login = (
            reverse('users:login') + '?next='
            + reverse('posts:add_comment', args=(self.post.id,))
        )
        self.assertRedirects(response, reverse_on_login)
        self.assertEqual(Comment.objects.count(), comment_count)

    def test_create_comment(self):
        """Проверка создания комментария."""
        comment_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', args=(self.post.id,)),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=(self.post.id,))
        )
        comment = Comment.objects.first()
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.assertEqual(comment.text, form_data['text'])
        self.assertEqual(comment.author, self.user)
