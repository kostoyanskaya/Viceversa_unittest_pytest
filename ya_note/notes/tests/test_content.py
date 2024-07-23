from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


ADD_URL = reverse('notes:add')
EDIT_URL = reverse('notes:edit', args=('note_slug',))
LIST_URL = reverse('notes:list')


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username='testauthor',
        )
        cls.reader = get_user_model().objects.create_user(
            username='testreader'
        )
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title='Название',
            text='Текст',
            author=cls.author,
            slug='note_slug',
        )

    def test_note_in_list(self):
        response = self.author_client.get(LIST_URL)
        self.assertIn(self.note, response.context['object_list'])

    def test_note_not_in_list(self):
        response = self.not_author_client.get(LIST_URL)
        self.assertNotIn(self.note, response.context['object_list'])

    def test_note_in_form(self):
        for url in (ADD_URL, EDIT_URL):
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
