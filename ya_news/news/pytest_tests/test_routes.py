from http import HTTPStatus

import pytest
from django.test.client import Client
from pytest_django.asserts import assertRedirects

HOME_URL = pytest.lazy_fixture('home_url')
DETAIL_URL = pytest.lazy_fixture('detail_url')
LOGIN_URL = pytest.lazy_fixture('login_url')
LOGOUT_URL = pytest.lazy_fixture('logout_url')
SIGN_UP_URL = pytest.lazy_fixture('sign_up_url')
EDIT_COMMENT_URL = pytest.lazy_fixture('edit_comment_url')
DELETE_COMMENT_URL = pytest.lazy_fixture('delete_comment_url')

ANONYMOUS_CLINET = Client()
AUTHOR_CLIENT = pytest.lazy_fixture('author_client')
NOT_AUTHOR_CLIENT = pytest.lazy_fixture('not_author_client')

pytestmark = pytest.mark.django_db


@pytest.mark.parametrize(
    'url, parametrized_client, expected_status',
    (
        (HOME_URL, ANONYMOUS_CLINET, HTTPStatus.OK),
        (DETAIL_URL, ANONYMOUS_CLINET, HTTPStatus.OK),
        (LOGIN_URL, ANONYMOUS_CLINET, HTTPStatus.OK),
        (LOGOUT_URL, ANONYMOUS_CLINET, HTTPStatus.OK),
        (SIGN_UP_URL, ANONYMOUS_CLINET, HTTPStatus.OK),
        (EDIT_COMMENT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (DELETE_COMMENT_URL, NOT_AUTHOR_CLIENT, HTTPStatus.NOT_FOUND),
        (EDIT_COMMENT_URL, AUTHOR_CLIENT, HTTPStatus.OK),
        (DELETE_COMMENT_URL, AUTHOR_CLIENT, HTTPStatus.OK)
    )
)
def test_pages_availability(url, parametrized_client, expected_status):
    """Главная страница доступна анонимному пользователю;
    Страница отдельной новости доступна анонимному пользователю;
    Страницы удаления и редактирования комментария доступны автору комментария;
    Авторизованный пользователь не может зайти на страницы редактирования
    или удаления чужих комментариев;
    Страницы регистрации пользователей, входа в учётную запись
    и выхода из неё доступны анонимным пользователям.
    """
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'url',
    (EDIT_COMMENT_URL, DELETE_COMMENT_URL)
)
def test_redirects(client, url, login_url):
    """При попытке перейти на страницу редактирования или удаления комментария
    анонимный пользователь перенаправляется на страницу авторизации.
    """
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
