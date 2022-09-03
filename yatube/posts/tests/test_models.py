from django.contrib.auth import get_user_model
from django.test import TestCase

from posts.models import Group, Post


User = get_user_model()


class PostModelTest(TestCase):
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
            group=cls.group
        )

    def test_models_have_correct_object_names(self):
        """Проверка object_names в посте."""
        post = PostModelTest.post
        self.assertEqual(post.text[:15], str(post))
        group = PostModelTest.group
        self.assertEqual(group.title, str(group))
        field_str = (
            (post.text[:15], str(post)),
            (group.title, str(group)),
        )
        for field, expected_value in field_str:
            with self.subTest(field=field):
                self.assertEqual(expected_value, field)

    def test_verbose_name_post(self):
        """Проверка verbose_name в посте."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата создания',
            'author': 'Автор',
            'group': 'Группа поста',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name,
                    expected_value)

    def test_verbose_name_group(self):
        """Проверка verbose_name в группе."""
        group = PostModelTest.group
        field_verboses = {
            'title': 'Название группы',
            'slug': 'Слаг группы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name,
                    expected_value)

    def test_help_text_post(self):
        """Проверка help_text в посте."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Введите текст поста',
            'group': 'Выберете группу для поста',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text,
                    expected_value)
