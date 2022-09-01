import shutil
import tempfile

from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.cache import cache
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
        )

        cls.revers_names_urls = (
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
             f'/posts/{cls.post.id}/comment/'),
            ('posts:follow_index', None, '/follow/'),
            ('posts:profile_follow', (cls.post.author,),
             f'/profile/{cls.post.author}/follow/'),
            ('posts:profile_unfollow', (cls.post.author,),
             f'/profile/{cls.post.author}/unfollow/'),
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_author = Client()
        self.authorized_author.force_login(self.post.author)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_revers_names_templates(self):
        self.revers_names_templates = (
            ('posts:index', None, 'posts/index.html'),
            ('posts:group_list', (self.group.slug,), 'posts/group_list.html'),
            ('posts:profile', (self.post.author,), 'posts/profile.html'),
            ('posts:post_detail', (self.post.id,), 'posts/post_detail.html'),
            ('posts:post_create', None, 'posts/create_post.html'),
            ('posts:post_edit', (self.post.id,), 'posts/create_post.html'),
            ('posts:follow_index', None, 'posts/follow.html'),
        )
        for name, args, template in self.revers_names_templates:
            with self.subTest(name=name):
                response = self.authorized_author.get(reverse(name, args=args))
                self.assertTemplateUsed(response, template)

    def test_urls_uses_correct_reverse_names(self):
        for name, args, url, in self.revers_names_urls:
            with self.subTest(name=name):
                self.assertEqual(reverse(name, args=args), url)

    def test_urls_for_anonymous(self):
        for name, args, url in self.revers_names_urls:
            with self.subTest(name=name):
                response = self.client.get(url, follow=True)
                if name in ['posts:post_create',
                            'posts:post_edit',
                            'posts:add_comment',
                            'posts:follow_index',
                            'posts:profile_follow',
                            'posts:profile_unfollow'
                            ]:
                    reverse_on_login = reverse('users:login') + '?next=' + url
                    self.assertRedirects(response, reverse_on_login)
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_for_authorized_client(self):
        for name, args, url in self.revers_names_urls:
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
        for name, args, url in self.revers_names_urls:
            with self.subTest(name=name):
                response = self.authorized_author.get(url, follow=True)
                if name == 'posts:profile_follow':
                    self.assertRedirects(
                        response,
                        reverse('posts:profile', args=args)
                    )
                elif name == 'posts:profile_unfollow':
                    self.assertEqual(response.status_code,
                                     HTTPStatus.NOT_FOUND
                                     )
                else:
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_page_404(self):
        response = self.client.get('/nonexist-page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, 'core/404.html')
