from datetime import datetime
import pytest

from pytest_django.asserts import assertRedirects
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from http import HTTPStatus

from news.models import Comment, News


User = get_user_model()


@pytest.fixture
def news():
    news = News.objects.create(
        title='Новость',
        text='Текст новости',
        date=datetime.today(),
    )
    return news


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария',
        created=datetime.now()
    )
    return comment


@pytest.fixture
def comment_delete(comment):
    return reverse('news:delete', args=(comment.id,))


@pytest.fixture
def comment_edit(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def news_pk(news):
    return news.id,


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:detail', pytest.lazy_fixture('news_pk')),
    )
)
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',

    (
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name',
    (
        (pytest.lazy_fixture('comment_delete')),
        (pytest.lazy_fixture('comment_edit')),
    ),
)
def test_pages_availability_for_different_users(
        parametrized_client, name, expected_status
):
    response = parametrized_client.get(name)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (
        (pytest.lazy_fixture('comment_delete')),
        (pytest.lazy_fixture('comment_edit')),
    ),
)
def test_pages_redirects(client, name):
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={name}'
    response = client.get(name)
    assertRedirects(response, expected_url)
