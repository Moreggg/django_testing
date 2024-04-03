import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(author_client, author, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, news):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(author_client, comment, news):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    assertRedirects(response,
                    f'{reverse("news:detail", args=(news.id,))}#comments')
    assert Comment.objects.count() == 0


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(author_client, form_data, comment, news):
    url = reverse('news:edit', args=(comment.id,))
    response = author_client.post(url, form_data)
    assertRedirects(response,
                    f'{reverse("news:detail", args=(news.id,))}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']


def test_user_cant_edit_comment_of_another_user(
        not_author_client, form_data, comment
):
    url = reverse('news:edit', args=(comment.id,))
    response = not_author_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
