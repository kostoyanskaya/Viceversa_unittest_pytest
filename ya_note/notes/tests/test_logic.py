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
        cls.note = {
            'text': 'Текст',
            'title': 'Название',
            'slug': 'note_slug',
        }

    def test_user_can_create_note(self):
        """Залогиненный пользователь может создать заметку."""
        Note.objects.all().delete()
        response = self.author_client.post(ADD_URL, data=self.note)
        self.assertRedirects(response, SUCCESS_URL)
        note = Note.objects.first()
        self.assertEqual(Note.objects.count(), 1)
        self.assertEqual(note.title, 'Название')
        self.assertEqual(note.text, 'Текст')
        self.assertEqual(note.slug, 'note_slug')

    def test_anonymous_not_create_note(self):
        """Анонимный пользователь может создать заметку."""
        initial_count = Note.objects.count()
        response = self.client.post(ADD_URL, data=self.note)
        result = f"{LOGIN_URL}?next={ADD_URL}"
        self.assertRedirects(response, result)
        self.assertEqual(Note.objects.count(), initial_count)

    def test_cannot_create_two_notes_with_same_slug(self):
        """Нельзя создать заметку с существующим slug."""
        Note.objects.create(author=self.author, **self.note)
        form_data = {
            'title': 'Title 2',
            'text': 'Текст',
            'slug': 'note_slug'
        }
        response = self.not_author_client.post(ADD_URL, data=form_data)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(Note.objects.count(), 1)

    def test_slug_generation(self):
        """Если при создании заметки не заполнен slug,
        то он формируется автоматически.
        """
        self.note.pop('slug')
        self.author_client.post(ADD_URL, data=self.note)
        notes_count = Note.objects.count()
        new_note = Note.objects.get()
        expected_slug = slugify(self.note['title'])
        self.assertEqual(notes_count, 1)
        self.assertEqual(new_note.slug, expected_slug)

    def test_author_can_edit_note(self):
        """Автор может редактировать свою заметку."""
        note_one = Note.objects.create(author=self.author, **self.note)
        response = self.author_client.post(EDIT_URL, data={
            'title': 'Измененная заметка',
            'text': 'Обновленный текст заметки'
        })
        self.assertRedirects(response, SUCCESS_URL)
        updated_note = Note.objects.get(id=note_one.id)
        self.assertEqual(updated_note.title, 'Измененная заметка')
        self.assertEqual(updated_note.text, 'Обновленный текст заметки')

    def test_anonymous_user_cant_edit_note(self):
        """Читатель не может редактировать чужие заметки."""
        note = Note.objects.create(author=self.author, **self.note)
        response = self.not_author_client.post(EDIT_URL, data=self.note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=note.id)
        self.assertEqual(note.title, note_from_db.title)
        self.assertEqual(note.text, note_from_db.text)

    def test_author_can_delete_note(self):
        """Автор может удалять свои заметки."""
        note_one = Note.objects.create(author=self.author, **self.note)
        response = self.author_client.post(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertFalse(Note.objects.filter(id=note_one.id).exists())

    def test_anonymous_user_cant_delete_note(self):
        """Читатель не может удалять чужие заметки."""
        note_one = Note.objects.create(author=self.author, **self.note)
        response = self.not_author_client.post(DELETE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(id=note_one.id).exists())
