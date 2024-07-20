from django.test import Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username='testauthor',
        )
        cls.reader = get_user_model().objects.create_user(
            username='testreader'
        )
        cls.note = Note.objects.create(
            title="Название",
            text="Текст",
            author=cls.author,
            slug="note_slug",
        )

        cls.add = reverse('notes:add')
        cls.edit = reverse('notes:edit', args=('note_slug',))

    def test_note_in_list(self):
        client = Client()
        client.force_login(self.author)
        response = client.get(reverse('notes:list'))
        self.assertIn(self.note, response.context['object_list'])

    def test_note_not_in_list(self):
        client = Client()
        client.force_login(self.reader)
        response = client.get(reverse('notes:list'))
        self.assertNotIn(self.note, response.context['object_list'])

    def test_note_in_form(self):
        client = Client()
        for url in (self.add, self.edit):
            with self.subTest(url=url):
                client.force_login(self.author)
                response = client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)
