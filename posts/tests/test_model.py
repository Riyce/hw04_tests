from django.test import TestCase

from django.contrib.auth import get_user_model

from posts.models import Group, Post


class ModelsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        User.objects.create_user(username='Oleg')
        user = User.objects.get(username='Oleg')
        Post.objects.create(
            text='Тестовый текст с длиной больше 15 символов',
            author=user,
            pk=1,
        )
        cls.post = Post.objects.get(pk=1)
        Group.objects.create(
            title='Тестовая группа',
            description='Тестовое поисание',
            slug='test-task'
        )
        cls.group = Group.objects.get(slug='test-task')

    def test_group_verbose_name(self):
        group = ModelsTest.group
        verbose = group._meta.get_field('title').verbose_name
        self.assertEquals(verbose, 'Название группы')

    def test_group_name_is_title_fild(self):
        group = ModelsTest.group
        expected_object_name = group.title
        self.assertEquals(expected_object_name, str(group))

    def test_post_verbose_name(self):
        post = ModelsTest.post
        verbose = post._meta.get_field('text').verbose_name
        self.assertEquals(verbose, 'Текст')

    def test_post_text_is_title_fild(self):
        post = ModelsTest.post
        expected_object_name = post.text[:15]
        self.assertEquals(expected_object_name, str(post))
