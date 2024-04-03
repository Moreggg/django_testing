import pytest

from django.conf import settings

from django.urls import reverse

from news.forms import CommentForm


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home',),
)
def test_news_count(client, name, all_news):
    url = reverse(name)
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = object_list.count()
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:home',),
)
def test_news_order(client, name, all_news):
    url = reverse(name)
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert sorted_dates == all_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_news_for_args')),
    ),
)
def test_comments_order(client, name, args, all_comments):
    url = reverse(name, args=args)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    sorted_timestamps = sorted(all_timestamps)
    assert all_timestamps == sorted_timestamps


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_news_for_args')),
    ),
)
def test_anonymous_client_has_no_form(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert 'form' not in response.context


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:detail', pytest.lazy_fixture('id_news_for_args')),
    ),
)
def test_authorized_client_has_form(author_client, name, args):
    url = reverse(name, args=args)
    response = author_client.get(url)
    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
