from django.test import Client, TestCase

from django.contrib.auth import get_user_model

from django.contrib.flatpages.models import FlatPage, Site

from posts.models import Group, Post

from django.urls import reverse


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        User = get_user_model()
        cls.guest_client = Client()
        cls.user1 = User.objects.create_user(username='Oleg')
        cls.user2 = User.objects.create_user(username='Olegson')
        cls.user = User.objects.get(username='Oleg')
        cls.author = Client()
        cls.author.force_login(cls.user1)
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user2)
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
        cls.post = Post.objects.get(pk=1)
        Group.objects.create(
            title='Тестовая группа',
            description='Тестовое описание группы',
            slug='test-slug'
        )
        cls.group = Group.objects.get(slug='test-slug')

    def test_pages_for_client(self):
        status_codes = {
            reverse('index'): 200,
            reverse('new_post'): 302,
            reverse(
                'group',
                kwargs={'slug': StaticURLTests.group.slug, }
            ):
            200,
            reverse(
                'profile',
                kwargs={'username': StaticURLTests.user.username, }
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
                response = StaticURLTests.guest_client.get(reversed_name)
                self.assertEqual(response.status_code, code)

    def test_pages_for_user(self):
        status_codes = {
            reverse('index'): 200,
            reverse('new_post'): 200,
            reverse(
                'group',
                kwargs={'slug': StaticURLTests.group.slug, }
            ):
            200,
            reverse(
                'profile',
                kwargs={'username': StaticURLTests.user.username, }
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
                response = StaticURLTests.authorized_client.get(reversed_name)
                self.assertEqual(response.status_code, code)

    def test_reditect_from_edit_page(self):
        redirects = {
            StaticURLTests.guest_client:
            reverse(
                'post',
                kwargs={
                    'username': StaticURLTests.user.username,
                    'post_id': StaticURLTests.post.pk
                }
            ),
            StaticURLTests.authorized_client:
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
        response = StaticURLTests.author.get(
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
                response = StaticURLTests.author.get(url)
                self.assertTemplateUsed(response, template)
