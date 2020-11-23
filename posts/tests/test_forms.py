from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from posts.forms import PostForm
from posts.models import Post
from django.urls import reverse

class PostFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        User.objects.create_user(username='Oleg')
        cls.user = User.objects.get(id=1)
        Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )
        cls.post = Post.objects.get(pk=1)
        cls.form = PostForm()
    
    def setUp(self):
        self.guest_client = Client()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_help_texts(self):
        help_texts = {
            'group': 'Выберете группу из списка доступных.',
            'text': 'Введите текст Вашего поста.',
        }
        for field, value in help_texts.items():
            with self.subTest():
                help_text = PostFormTests.form.fields[field].help_text
                self.assertEqual(help_text, value)

    def test_labels(self):
        labels = {
            'group': 'Выберете группу',
            'text': 'Текст',
        }
        for field, value in labels.items():
            with self.subTest():
                label = PostFormTests.form.fields[field].label
                self.assertEqual(label, value)

    def test_create_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый текст',
        }
        response = self.authorized_client.post(
            reverse('new_post'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse('index'))
        self.assertEqual(Post.objects.count(), posts_count + 1)

    def test_edit_post(self):
        form_data = {
            'text': 'Тестовый текст измененный',
        }
        response = self.authorized_client.post(
            reverse(
                'post_edit', 
                kwargs={
                    'username': PostFormTests.user,
                    'post_id': PostFormTests.post.pk,
                }
            ),
            data=form_data,
            follow=True,
        )
        self.assertEqual(
            Post.objects.get(pk=1).text, 
            'Тестовый текст измененный'
        )     
