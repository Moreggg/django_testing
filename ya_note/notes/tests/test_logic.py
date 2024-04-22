from http import HTTPStatus
from pytils.translit import slugify

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note
from notes.forms import WARNING

User = get_user_model()

SLUG = 'slug'

ADD_NOTE_URL = reverse('notes:add')
EDIT_NOTE_URL = reverse('notes:edit', args=(SLUG,))
DELETE_NOTE_URL = reverse('notes:delete', args=(SLUG,))
SUCCESS_URL = reverse('notes:success')


class TestNoteCreation(TestCase):
    NOTE_TITLE = 'title'
    NOTE_TEXT = 'Текст'
    NOTE_SLUG = SLUG

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create(username='Автор')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {
            'text': cls.NOTE_TEXT,
            'title': cls.NOTE_TITLE,
            'slug': cls.NOTE_SLUG
        }

    def test_anonymous_user_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        notes_count_before = Note.objects.count()
        self.client.post(ADD_NOTE_URL, data=self.form_data)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        Note.objects.all().delete()
        notes_count_before = Note.objects.count()
        response = self.auth_client.post(ADD_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before + 1, notes_count_after)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.user)

    def test_empty_slug(self):
        """Если slug не заполнен, то он формируется автоматически."""
        Note.objects.all().delete()
        notes_count_before = Note.objects.count()
        self.assertEqual(notes_count_before, 0)
        self.form_data.pop('slug')
        response = self.auth_client.post(ADD_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before + 1, notes_count_after)
        note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.author, self.user)


class TestCommentEditDelete(TestCase):
    NOTE_TITLE = 'title'
    NOTE_TEXT = 'Текст'
    NOTE_SLUG = SLUG
    NEW_NOTE_TEXT = 'New text'
    NEW_NOTE_TITLE = 'New title'

    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.note = Note.objects.create(
            title=cls.NOTE_TITLE,
            text=cls.NOTE_TEXT,
            slug=cls.NOTE_SLUG,
            author=cls.author,
        )
        cls.form_data = {
            'text': cls.NEW_NOTE_TEXT,
            'title': cls.NEW_NOTE_TITLE,
            'slug': cls.NOTE_SLUG
        }

    def test_not_unique_slug(self):
        """Невозможно создать две заметки с одинаковым slug."""
        notes_count_before = Note.objects.count()
        response = self.author_client.post(ADD_NOTE_URL, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.note.slug + WARNING
        )
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_author_can_delete_note(self):
        """Пользователь может удалить свою заметку."""
        notes_count_before = Note.objects.count()
        response = self.author_client.delete(DELETE_NOTE_URL)
        self.assertRedirects(response, SUCCESS_URL)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_before - 1, notes_count_after)

    def test_user_cant_delete_note_of_another_user(self):
        """Пользователь не может удалить чужую заметку."""
        notes_count_before = Note.objects.count()
        response = self.reader_client.delete(DELETE_NOTE_URL)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        notes_count_after = Note.objects.count()
        self.assertEqual(notes_count_after, notes_count_before)

    def test_author_can_edit_note(self):
        """Пользователь может редактировать свою заметку."""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.author_client.post(EDIT_NOTE_URL, data=self.form_data)
        self.assertRedirects(response, SUCCESS_URL)
        note = Note.objects.get()
        self.assertEqual(note.title, self.form_data['title'])
        self.assertEqual(note.text, self.form_data['text'])
        self.assertEqual(note.slug, self.form_data['slug'])
        self.assertEqual(note.author, self.author)

    def test_user_cant_edit_note_of_another_user(self):
        """Пользователь не может редактировать чужую заметку."""
        notes_count = Note.objects.count()
        self.assertEqual(notes_count, 1)
        response = self.reader_client.post(EDIT_NOTE_URL, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        note = Note.objects.get()
        self.assertEqual(note.title, self.note.title)
        self.assertEqual(note.text, self.note.text)
        self.assertEqual(note.slug, self.note.slug)
        self.assertEqual(note.author, self.note.author)
