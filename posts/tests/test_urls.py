from django.test import Client, TestCase
from django.contrib.auth import get_user_model
from posts.models import Group ,Post
from django.urls import reverse
from django.contrib.flatpages.models import FlatPage, Site

class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        User.objects.create_user(username='Oleg')
        cls.user = User.objects.get(id=1)
        cls.site = Site.objects.get(pk=2)
        cls.site.save()
        cls.flat_about = FlatPage.objects.create(
            url='/about-author/',
            title='about me',
            content='<b>content</b>'
        )
        cls.flat_about.save()
        cls.flat_tech = FlatPage.objects.create(
            url='/about-spec/',
            title='about my tech',
            content='<b>content</b>'
        )
        cls.flat_tech.save()
        cls.flat_about.sites.add(cls.site)
        cls.flat_tech.sites.add(cls.site)
        Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            pk=1,
        )
        Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание группы',
            slug='test-slug'
        )
        cls.group = Group.objects.get(pk=1)
        cls.post = Post.objects.get(pk=1)
        
    def setUp(self):
        self.guest_client = Client()
        self.user1 = get_user_model().objects.create_user(
            username='Olegson'
        )
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user1)
        self.author = Client()
        self.author.force_login(StaticURLTests.user)

    def test_pages_for_client(self):
        status_codes = {
            reverse('index'): 200,
            reverse('new_post'): 302,
            reverse(
                'group',
                kwargs={'slug': StaticURLTests.group.slug,}
            ):
            200,
            reverse(
                'profile',
                kwargs={'username': StaticURLTests.user.username,}
            ): 
            200,
            reverse(
                'post',
                kwargs={
                    'username': StaticURLTests.user.username,
                    'post_id': StaticURLTests.post.pk
                }
            ):
            200,
            reverse(
                'post_edit',
                kwargs={
                    'username': StaticURLTests.user.username,
                    'post_id': StaticURLTests.post.pk
                }
            ):
            302,
            reverse('about'): 200,
            reverse('about-spec'): 200,
        }
        for reversed_name, code in status_codes.items():
            with self.subTest():
                response = self.guest_client.get(reversed_name)
                self.assertEqual(response.status_code, code) 

    def test_pages_for_user(self):
        status_codes = {
            reverse('index'): 200,
            reverse('new_post'): 200,
            reverse(
                'group',
                kwargs={'slug': StaticURLTests.group.slug,}
            ): 
            200,
            reverse(
                'profile',
                kwargs={'username': StaticURLTests.user.username,}
            ):
            200,
            reverse(
                'post',
                kwargs={
                    'username':
                    StaticURLTests.user.username,
                    'post_id': StaticURLTests.post.pk
                }
            ):
            200,
            reverse(
                'post_edit',
                kwargs={
                    'username': StaticURLTests.user.username,
                    'post_id': StaticURLTests.post.pk
                }
            ):
            302,
            reverse('about'): 200,
            reverse('about-spec'): 200,
        }
        for reversed_name, code in status_codes.items():
            with self.subTest():
                response = self.authorized_client.get(reversed_name)
                self.assertEqual(response.status_code, code)
            
    def test_reditect_from_edit_page(self):
        redirects = {
            self.guest_client:
            reverse(
                'post',
                kwargs={
                    'username': StaticURLTests.user.username,
                    'post_id': StaticURLTests.post.pk
                }
            ),
            self.authorized_client:
            reverse(
                'post',
                kwargs={
                    'username': StaticURLTests.user.username,
                    'post_id': StaticURLTests.post.pk
                }
            ),
        }
        for users, adress in redirects.items():
            with self.subTest():
                response = users.post(
                    reverse(
                        'post_edit',
                        kwargs={
                            'username': StaticURLTests.user.username,
                            'post_id': StaticURLTests.post.pk
                        }
                    )
                )
                self.assertRedirects(response, adress)
    
    def test_edit_post_page_for_author(self):
        response = self.author.get(
            reverse(
                'post_edit',
                kwargs={
                    'username': StaticURLTests.user.username,
                    'post_id': StaticURLTests.post.pk
                }
            )
        )
        self.assertEqual(response.status_code, 200)

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            '/': 'index.html',
            '/new/': 'new.html',
            '/group/test-slug/': 'group.html',
            '/Oleg/1/edit/': 'new.html',
            '/about-author/': 'flatpages/default.html',
            '/about-spec/': 'flatpages/default.html',
            '/Oleg/': 'profile.html',
        }
        for url, template in templates_url_names.items():
            with self.subTest():
                response = self.author.get(url)
                self.assertTemplateUsed(response, template)
