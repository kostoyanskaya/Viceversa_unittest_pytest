from http import HTTPStatus

from django.test import Client
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytils.translit import slugify

from notes.models import Note


User = get_user_model()

ADD_URL = reverse('notes:add')
SUCCESS_URL = reverse('notes:success')
LOGIN_URL = reverse('users:login')
EDIT_URL = reverse('notes:edit', args=('note_slug',))
DELETE_URL = reverse('notes:delete', args=('note_slug',))


class LogicContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username='testauthor'
        )

        cls.reader = get_user_model().objects.create_user(
            username='testuser'
        )
        cls.client = Client()
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.reader)
        cls.note_data = {
            'text': 'Текст',
            'title': 'Название',
            'slug': 'note_slug',
        }
        cls.note = Note.objects.create(author=cls.author, **cls.note_data)

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        response = self.author_client.post(ADD_URL, data=self.note_data)
        self.assertRedirects(response, SUCCESS_URL)
        note = Note.objects.first()
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(note.title, self.note_data['title'])
        self.assertEqual(note.text, self.note_data['text'])
        self.assertEqual(note.slug, self.note_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_anonymous_not_create_note(self):
        """Анонимный пользователь может создать заметку."""
        initial_count = Note.objects.count()
        response = self.client.post(ADD_URL, data=self.note_data)
        result = f"{LOGIN_URL}?next={ADD_URL}"
        self.assertRedirects(response, result)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_cannot_create_two_notes_with_same_slug(self):
        """Нельзя создать заметку с существующим slug."""
        initial_count = Note.objects.count()
        response = self.not_author_client.post(ADD_URL, data=self.note_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_slug_generation(self):
        """Поле slug формируется автоматически."""
        self.note_data.pop('slug')
        Note.objects.all().delete()
        initial_count = Note.objects.count()
        self.author_client.post(ADD_URL, data=self.note_data)
        new_note = Note.objects.get()
        expected_slug = slugify(self.note_data['title'])
        self.assertEqual(Note.objects.count(), initial_count + 1)
        self.assertEqual(new_note.slug, expected_slug)
        self.assertEqual(new_note.title, self.note_data['title'])
        self.assertEqual(new_note.text, self.note_data['text'])
        self.assertEqual(new_note.author, self.author)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        initial_count = Note.objects.count()
        response = self.author_client.post(EDIT_URL, data=self.note_data)
        self.assertRedirects(response, SUCCESS_URL)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, self.note_data['title'])
        self.assertEqual(updated_note.text, self.note_data['text'])
        self.assertEqual(updated_note.author, self.note.author)
        self.assertEqual(updated_note.slug, self.note_data['slug'])
        self.assertEqual(Note.objects.count(), initial_count)

    def test_anonymous_user_cant_edit_note(self):
        """Читатель не может редактировать чужие заметки."""
        initial_count = Note.objects.count()
        response = self.not_author_client.post(EDIT_URL, data=self.note_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=self.note.id)
        self.assertEqual(note_from_db.title, self.note_data['title'])
        self.assertEqual(note_from_db.text, self.note_data['text'])
        self.assertEqual(note_from_db.author, self.note.author)
        self.assertEqual(note_from_db.slug, self.note_data['slug'])
        self.assertEqual(Note.objects.count(), initial_count)

    def test_author_can_delete_note(self):
        """Автор может удалять свои заметки."""
        initial_count = Note.objects.count()
        response = self.author_client.post(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertFalse(Note.objects.filter(id=self.note.id).exists())
        self.assertEqual(Note.objects.count(), initial_count - 1)

    def test_anonymous_user_cant_delete_note(self):
        """Читатель не может удалять чужие заметки."""
        initial_count = Note.objects.count()
        response = self.not_author_client.post(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=self.note.id).exists())
        self.assertEqual(Note.objects.count(), initial_count)
