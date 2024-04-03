from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from notes.models import Note
from notes.forms import NoteForm

User = get_user_model()


class TestNotesPages(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = User.objects.create(username='Автор')
        cls.another_author = User.objects.create(username='Другой автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=cls.author
        )

    def test_notes_list_for_author_user(self):
        url = reverse('notes:list')
        self.client.force_login(self.author)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertIn(self.note, object_list)

    def test_notes_list_for_non_author_user(self):
        url = reverse('notes:list')
        self.client.force_login(self.another_author)
        response = self.client.get(url)
        object_list = response.context['object_list']
        self.assertNotIn(self.note, object_list)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(reverse('notes:add'))
        self.assertIsNone(response.context)

    def test_authorized_client_has_form(self):
        self.client.force_login(self.author)
        response = self.client.get(reverse('notes:add'))
        self.assertIn('form', response.context)
        self.assertIsInstance(response.context['form'], NoteForm)
