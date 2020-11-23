from django.contrib.auth import get_user_model
from django.forms.fields import DateTimeField
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post
from django import forms
from django.contrib.flatpages.models import FlatPage, Site

class PagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание группы',
            slug='test-slug'
        )
        cls.site = Site.objects.get(pk=2)
        cls.site.save()
        cls.flat_about = FlatPage.objects.create(
            url='/about-author/',
            title='Об авторе',
            content='<b>Здесь текст про автора</b>'
        )
        cls.flat_about.save()
        cls.flat_tech = FlatPage.objects.create(
            url='/about-spec/',
            title='О технологиях',
            content='<b>Здесь текст про технологии</b>'
        )
        cls.flat_tech.save()
        cls.flat_about.sites.add(cls.site)
        cls.flat_tech.sites.add(cls.site)
        Group.objects.create(
            title='Тестовая группа 2',
            description='Тестовое описание группы 2',
            slug='test-slug2'
        )
        cls.group1 = Group.objects.get(pk=1)
        cls.group2 = Group.objects.get(pk=2)

    def setUp(self):
        self.guest_client = Client()
        User = get_user_model()
        self.user = User.objects.create_user(username='Oleg')
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        user = User.objects.get(pk=1)
        Post.objects.create(
            text='Тестовый текст',
            group=PagesTests.group1,
            author=user,
        )
        self.post = Post.objects.get(text='Тестовый текст')

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            'index.html': reverse('index'),
            'new.html': reverse('new_post'), 
            'group.html': 
            reverse('group', kwargs={'slug': PagesTests.group1.slug}),
            'profile.html': 
            reverse('profile', kwargs={'username': self.user.username}),
            'post.html':
            reverse(
                'post', 
                kwargs={
                    'username': self.post.author.username, 
                    'post_id': self.post.pk
                }
            )
        }
        for template, reverse_name in templates_pages_names.items():
            with self.subTest():
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template) 

    def test_home_page_shows_correct_context(self):
        response = self.authorized_client.get(reverse('index'))
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author
        post_group = response.context.get('page')[0].group
        post_pub_date = response.context.get('page')[0].pub_date
        paginator = response.context.get('paginator').per_page
        posts_count = response.context.get('paginator').count
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_pub_date, self.post.pub_date)
        self.assertEqual(paginator, 10)
        self.assertEqual(posts_count, 1)

    def test_group_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('group', kwargs={'slug': 'test-slug'})
        )
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author
        post_group = response.context.get('page')[0].group
        post_pub_date = response.context.get('page')[0].pub_date
        paginator = response.context.get('paginator').per_page
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_pub_date, self.post.pub_date)
        self.assertEqual(paginator, 10)

    def test_new_post_shows_correct_context(self):
        response = self.authorized_client.get(reverse('new_post'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }        
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post_edit', 
                kwargs={
                    'username': self.post.author, 
                    'post_id': self.post.pk
                }
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }        
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
            
    def test_profile_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse('profile', kwargs={'username': self.user.username})
        )
        post_text = response.context.get('page')[0].text
        post_author = response.context.get('page')[0].author
        post_group = response.context.get('page')[0].group
        post_pub_date = response.context.get('page')[0].pub_date
        author_username = response.context.get('author').username
        author_posts_count = response.context.get('author').posts.count()
        paginator = response.context.get('paginator').per_page
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_pub_date, self.post.pub_date)
        self.assertEqual(author_username, self.user.username)
        self.assertEqual(author_posts_count, self.user.posts.count())
        self.assertEqual(paginator, 10)

    def test_post_page_shows_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'post', 
                kwargs={
                    'username': self.post.author.username, 
                    'post_id': self.post.pk
                }
            )
        )
        post_text = response.context.get('post').text
        post_author = response.context.get('post').author
        post_group = response.context.get('post').group
        post_pub_date = response.context.get('post').pub_date
        author_username = response.context.get('author').username
        author_posts_count = response.context.get('author').posts.count()
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_author, self.post.author)
        self.assertEqual(post_group, self.post.group)
        self.assertEqual(post_pub_date, self.post.pub_date)
        self.assertEqual(author_username, self.user.username)
        self.assertEqual(author_posts_count, self.user.posts.count())

    def test_flatpages_page_shows_correct_context(self):
        response1 = self.authorized_client.get('/about-author/')
        response2 = self.authorized_client.get('/about-spec/')
        author_title = response1.context.get('flatpage').title
        spec_title = response2.context.get('flatpage').title
        author_content = response1.context.get('flatpage').content
        spec_content = response2.context.get('flatpage').content
        self.assertEqual(author_title, 'Об авторе')
        self.assertEqual(spec_title, 'О технологиях')
        self.assertEqual(author_content, '<b>Здесь текст про автора</b>')
        self.assertEqual(spec_content, '<b>Здесь текст про технологии</b>')

    def test_post_goes_to_correct_group(self):
        response1 = self.authorized_client.get(
            reverse('group', kwargs={'slug': PagesTests.group1.slug})
        )
        response2 = self.authorized_client.get(
            reverse('group', kwargs={'slug': PagesTests.group2.slug})
        )
        paginator1 = response1.context.get('paginator').count
        paginator2 = response2.context.get('paginator').count
        self.assertEqual(paginator1, 1)
        self.assertEqual(paginator2, 0)
        self.assertEqual(PagesTests.group1.posts.count(), 1)
        self.assertEqual(PagesTests.group2.posts.count(), 0)
