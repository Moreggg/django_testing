from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import BAD_WORDS, WARNING
from news.models import Comment


def test_user_can_create_comment(
        author_client, author, form_data, news, detail_url
):
    """Авторизованный пользователь может отправить комментарий."""
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_after == comments_count_before + 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.news == news
    assert comment.author == author


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(
    client, form_data, detail_url, login_url
):
    """Анонимный пользователь не может отправить комментарий."""
    comments_count_before = Comment.objects.count()
    response = client.post(detail_url, data=form_data)
    expected_url = f'{login_url}?next={detail_url}'
    assertRedirects(response, expected_url)
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after


def test_user_cant_use_bad_words(author_client, detail_url):
    """Если комментарий содержит запрещённые слова, он не будет опубликован,
    а форма вернёт ошибку.
    """
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    comments_count_before = Comment.objects.count()
    response = author_client.post(detail_url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after


def test_author_can_delete_comment(
        author_client, delete_comment_url, detail_url
):
    """Автор может удалить свой комментарий."""
    comments_count_before = Comment.objects.count()
    response = author_client.post(delete_comment_url)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_before - 1 == comments_count_after


def test_user_cant_delete_comment_of_another_user(
        not_author_client, delete_comment_url
):
    """Пользователь не может удалить чужой комментарий."""
    comments_count_before = Comment.objects.count()
    response = not_author_client.post(delete_comment_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after


def test_author_can_edit_comment(
        author_client, form_data, comment, edit_comment_url, detail_url
):
    """Автор может редактировать свой комментарий."""
    comments_count_before = Comment.objects.count()
    response = author_client.post(edit_comment_url, form_data)
    assertRedirects(response, f'{detail_url}#comments')
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after
    edited_comment = Comment.objects.get()
    assert edited_comment.text == form_data['text']
    assert edited_comment.news == comment.news
    assert edited_comment.author == comment.author
    assert edited_comment.created == comment.created


def test_user_cant_edit_comment_of_another_user(
        not_author_client, form_data, comment, edit_comment_url
):
    """Пользователь не может редактировать чужой комментарий."""
    comments_count_before = Comment.objects.count()
    response = not_author_client.post(edit_comment_url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count_after = Comment.objects.count()
    assert comments_count_before == comments_count_after
    comment_from_db = Comment.objects.get()
    assert comment.text == comment_from_db.text
    assert comment.news == comment_from_db.news
    assert comment.author == comment_from_db.author
    assert comment.created == comment_from_db.created
