import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from django import forms
from django.core.cache import cache

from posts.forms import PostForm
from posts.models import Comment, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewsTests(TestCase):
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
            author=cls.user,
            text='Текст тестового поста',
            group=cls.group,
        )
        cls.comments = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='Тестовый комментарий'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def correct_context(self, response, check=False):
        if check:
            post = response.context.get('post')
        else:
            post = response.context.get('page_obj')[0]
        self.fields = (
            (post.text, self.post.text),
            (post.author, self.user),
            (post.pub_date, self.post.pub_date),
            (post.group, self.post.group),
            (post.comments, self.post.comments),
            (post.image, self.post.image)
        )
        for field, correct_field in self.fields:
            with self.subTest(field=field):
                self.assertEqual(field, correct_field)

    def test_index_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.correct_context(response)

    def test_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list', args=(self.group.slug,)))
        self.correct_context(response)
        fields_group_list = (
            (response.context.get('group').title, self.group.title),
            (response.context.get('group').slug, self.group.slug),
            (response.context.get('group').description,
             self.group.description),
        )
        for first_object, value in fields_group_list:
            with self.subTest():
                self.assertEqual(first_object, value)

    def test_group_list_another_group(self):
        new_post = self.post
        new_group = Group.objects.create(
            title='name new group',
            slug='new_test_slug',
            description='description new group',
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', args=(new_group.slug,)))
        self.assertEqual(len(response.context.get('page_obj')), 0)
        self.assertTrue(new_post.group)
        response = self.authorized_client.get(reverse(
            'posts:group_list', args=(self.group.slug,)))
        self.assertEqual(response.context.get('page_obj')[0].text,
                         self.post.text)

    def test_profile_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:profile', args=(self.user.username,)))
        self.correct_context(response)
        self.assertEqual(response.context.get('author'),
                         self.user)

    def test_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(reverse(
            'posts:post_detail', args=(self.post.id,)))
        self.correct_context(response, True)

    def test_post_create_page_show_correct_context(self):
        form_fields = (
            ('text', forms.fields.CharField),
            ('group', forms.fields.ChoiceField),
        )
        names_args = (
            ('posts:post_create', None),
            ('posts:post_edit', (self.post.id,)),
        )
        for names, args in names_args:
            with self.subTest():
                response = self.authorized_client.get(reverse(names,
                                                              args=args))
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context.get('form'), PostForm)
                for value, expected in form_fields:
                    with self.subTest(value=value):
                        form_field = response.context.get('form').fields.get(
                            value)
                        self.assertIsInstance(form_field, expected)

    def test_comment_show_in_post_detail(self):
        response = self.client.get(
            reverse('posts:post_detail', args=(self.post.id,))
        )
        self.assertContains(response, self.comments.text)

    def test_index_cache(self):
        new_post = Post.objects.create(
            text='text_test_post_cache',
            author=self.user
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.correct_context(response)
        new_post.delete()
        response_cache = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.content, response_cache.content)
        cache.clear()
        response_cache_clear = self.authorized_client.get(
            reverse('posts:index'))
        self.assertNotEqual(response_cache.content,
                            response_cache_clear.content)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='title_group',
            slug='test_slug',
            description='description_group',
        )
        pages = []
        for page in range(settings.LIMIT + settings.TEST_PAGES):
            pages.append(Post(author=cls.user,
                              text=f'Текст тестового поста {page}',
                              group=cls.group,
                              )
                         )
        cls.post = Post.objects.bulk_create(pages)

    def setUp(self):
        pass

    def test_paginator(self):
        urls = (
            ('posts:index', None),
            ('posts:group_list', (self.group.slug,)),
            ('posts:profile', (self.user.username,)),
        )
        pages = (
            ('?page=1', settings.LIMIT),
            ('?page=2', settings.TEST_PAGES),
        )
        for name, args in urls:
            with self.subTest():
                for page, amount in pages:
                    with self.subTest():
                        response = self.client.get(reverse(name, args=args)
                                                   + page)
                        self.assertEqual(len(response.context['page_obj']),
                                         amount)
