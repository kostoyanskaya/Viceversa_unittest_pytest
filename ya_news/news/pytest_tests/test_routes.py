from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.contrib.auth import get_user_model


pytestmark = pytest.mark.django_db


User = get_user_model()

OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND

unnamed = pytest.lazy_fixture('client')
author = pytest.lazy_fixture('author_client')
not_author = pytest.lazy_fixture('not_author_client')


@pytest.mark.parametrize(
    'url, argument_client, expected_status',
    [
        (pytest.lazy_fixture('home_url'), unnamed, OK),
        (pytest.lazy_fixture('detail_url'), unnamed, OK),
        (pytest.lazy_fixture('login_url'), unnamed, OK),
        (pytest.lazy_fixture('logout_url'), unnamed, OK),
        (pytest.lazy_fixture('signup_url'), unnamed, OK),
        (pytest.lazy_fixture('edit_url'), author, OK),
        (pytest.lazy_fixture('delete_url'), author, OK),
        (pytest.lazy_fixture('edit_url'), not_author, NOT_FOUND),
        (pytest.lazy_fixture('delete_url'), not_author, NOT_FOUND),
    ],
)
def test_pages_availability_for_different_user(
        url, argument_client, expected_status):
    """Страницы доступные разным клиентам."""
    response = argument_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    (
        (pytest.lazy_fixture('comment_delete')),
        (pytest.lazy_fixture('comment_edit')),
    ),
)
def test_pages_redirects(client, name, login_url):
    """Редирект на страницу логина."""
    expected_url = f'{login_url}?next={name}'
    response = client.get(name)
    assertRedirects(response, expected_url)
