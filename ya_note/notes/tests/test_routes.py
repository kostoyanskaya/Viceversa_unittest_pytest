from http import HTTPStatus

from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from notes.models import Note

User = get_user_model()

HOME_URL = reverse('notes:home')
ADD_URL = reverse("notes:add")
SUCCESS_URL = reverse('notes:success')
LOGIN_URL = reverse('users:login')
EDIT_URL = reverse('notes:edit', args=('note_slug',))
DELETE_URL = reverse('notes:delete', args=('note_slug',))
LIST_URL = reverse('notes:list')
DETAIL_URL = reverse('notes:detail', args=('note_slug',))
LOGOUT_URL = reverse('users:logout')
SIGNUP_URL = reverse('users:signup')


class TestRoutes(TestCase):

    ALL_URLS = (
        HOME_URL,
        ADD_URL,
        SUCCESS_URL,
        LIST_URL,
        EDIT_URL,
        DELETE_URL,
        DETAIL_URL,
        LOGIN_URL,
        LOGOUT_URL,
        SIGNUP_URL
    )

    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(username='testuser')
        cls.reader = get_user_model().objects.create_user(username='testreader')
        cls.note = Note.objects.create(title='Заголовок', text='Текст', author=cls.author, slug='note_slug')

        cls.client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.reader)

    def test_all_urls_accessible_by_author(self):
        for url in self.ALL_URLS:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_accessibility_for_non_author(self):
        non_editable_urls = (EDIT_URL, DELETE_URL, DETAIL_URL)
        for url in self.ALL_URLS:
            with self.subTest(url=url):
                if url in non_editable_urls:
                    response = self.not_author_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                else:
                    response = self.not_author_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_redirect_for_anonymous_client(self):
        non_accessible_urls = (EDIT_URL, DELETE_URL, DETAIL_URL)
        for url in self.ALL_URLS:
            with self.subTest(url=url):
                if url in non_accessible_urls:
                    redirect_url = f'{LOGIN_URL}?next={url}'
                    response = self.client.get(url)
                    self.assertRedirects(response, redirect_url)
                else:
                    response = self.not_author_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)
