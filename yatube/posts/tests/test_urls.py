import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post


TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostUrlTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test_slug',
            description='Описание тестовой группы',
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_author'),
            text='Текст тестового поста',
            group=cls.group,
            image=cls.image,
        )

        cls.revers_names_urls_names = (
            ('posts:index', None, '/'),
            ('posts:group_list', (cls.group.slug,),
             f'/group/{cls.post.group.slug}/'),
            ('posts:profile', (cls.post.author,),
             f'/profile/{cls.post.author}/'),
            ('posts:post_detail', (cls.post.id,),
             f'/posts/{cls.post.id}/'),
            ('posts:post_create', None, '/create/'),
            ('posts:post_edit', (cls.post.id,),
             f'/posts/{cls.post.id}/edit/'),
            ('posts:add_comment', (cls.post.id,),
             f'/posts/{cls.post.id}/comment/')
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    def test_revers_names_templates(self):
        self.revers_names_templates = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_list', (self.group.slug,), 'posts/group_list.html'),
            ('posts:profile', (self.post.author,), 'posts/profile.html'),
            ('posts:post_detail', (self.post.id,), 'posts/post_detail.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
            ('posts:post_edit', (self.post.id,), 'posts/create_post.html'),
        )
        for name, args, template in self.revers_names_templates:
            with self.subTest(name=name):
                response = self.authorized_author.get(reverse(name, args=args))
                self.assertTemplateUsed(response, template)

    def test_page_404(self):
        response = self.client.get('/qwerty12345/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_urls_uses_correct_reverse_names(self):
        for name, args, url in self.revers_names_urls_names:
            with self.subTest(name=name):
                self.assertEqual(reverse(name, args=args), url)

    def test_urls_for_anonymous(self):
        for name, args, url in self.revers_names_urls_names:
            with self.subTest(name=name):
                response = self.client.get(url, follow=True)
                if name in ['posts:post_create',
                            'posts:post_edit',
                            'posts:add_comment'
                            ]:
                    reverse_on_login = reverse('users:login') + '?next=' + url
                    self.assertRedirects(response, reverse_on_login)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_authorized_client(self):
        for name, args, url in self.revers_names_urls_names:
            with self.subTest(name=name):
                response = self.authorized_client.get(url, follow=True)
                if name == 'posts:post_edit':
                    self.assertRedirects(
                        response,
                        reverse('posts:post_detail', args=args)
                    )
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_authorized_author(self):
        for name, args, url in self.revers_names_urls_names:
            with self.subTest(name=name):
                response = self.authorized_author.get(url, follow=True)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_with_image(self):
        urls = (
            ('posts:index', None),
            ('posts:group_list', (self.group.slug,),),
            ('posts:profile', (self.post.author,),),
            ('posts:post_detail', (self.post.id,),),
        )
        for url, args in urls:
            with self.subTest(url=url):
                response = self.authorized_author.get(reverse(url, args=args))
                self.assertEqual(response.context['post'].image,
                                 self.post.image
                                 )
