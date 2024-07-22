from http import HTTPStatus

from django.test import Client
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from notes.models import Note
from notes.forms import NoteForm


User = get_user_model()

ADD_URL = reverse("notes:add")
SUCCESS_URL = reverse("notes:success")
LOGIN_URL = reverse('users:login')
EDIT_URL = reverse('notes:edit', args=("note_slug",))
DELETE_URL = reverse('notes:delete', args=("note_slug",))


class LogicContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author = get_user_model().objects.create_user(
            username='testauthor'
        )

        cls.user = get_user_model().objects.create_user(
            username='testuser'
        )
        cls.client = Client()
        cls.users = Client()
        cls.note = {
            "text": "Текст",
            "title": "Название",
            "slug": "note_slug",
            "author": cls.author,
        }

    def test_user_can_create_note(self):
        self.client.force_login(self.author)
        response = self.client.post(ADD_URL, data=self.note)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertEqual(Note.objects.count(), 1)

    def test_anonymous_nt_create_note(self):
        response = self.client.post(ADD_URL, data=self.note)
        result = f"{LOGIN_URL}?next={ADD_URL}"
        self.assertRedirects(response, result)
        self.assertEqual(Note.objects.count(), 0)

    def test_cannot_create_two_notes_with_same_slug(self):
        note1 = Note.objects.create(
            title="Название",
            text="Текст",
            author=self.author,
            slug="note_slug",
        )
        note1.save()
        slug1 = note1.slug
        other_author = get_user_model().objects.create_user(
            username='other_author',
        )
        self.client.force_login(other_author)
        form_data = {
            'title': "Title 2", 'text': "Тексrgт",
            'author': other_author, 'slug': slug1
        }
        form = NoteForm(data=form_data)
        self.assertFalse(form.is_valid())
        notes = Note.objects.all()
        self.assertEqual(len(notes), 1)

    def test_slug_generation(self):
        self.client.force_login(self.user)
        note = Note.objects.create(
            title="Тестовая заметка",
            text="Это тестовая заметка.", author=self.user
        )
        self.assertEqual(note.slug, "testovaya-zametka")

    def test_author_can_edit_note(self):
        self.client.force_login(self.author)
        note_one = Note.objects.create(**self.note)
        response = self.client.post(EDIT_URL, data=self.note)
        self.assertRedirects(response, SUCCESS_URL)
        note_one.refresh_from_db()

    def test_anonymous_user_cant_edit_note(self):
        self.client.force_login(self.author)
        note = Note.objects.create(**self.note)
        self.users.force_login(self.user)
        response = self.users.post(EDIT_URL, self.note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note_from_db = Note.objects.get(id=note.id)
        self.assertEqual(note.title, note_from_db.title)

    def test_author_can_delete_note(self):
        self.client.force_login(self.author)
        note_one = Note.objects.create(**self.note)
        response = self.client.post(DELETE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        self.assertFalse(Note.objects.filter(slug=note_one.slug).exists())

    def test_anonymous_user_cant_delete_note(self):
        self.client.force_login(self.author)
        note_one = Note.objects.create(**self.note)
        self.users.force_login(self.user)
        response = self.users.post(DELETE_URL, data=self.note)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTrue(Note.objects.filter(slug=note_one.slug).exists())
