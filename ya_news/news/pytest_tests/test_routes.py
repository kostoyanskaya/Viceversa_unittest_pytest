from http import HTTPStatus

import pytest
from pytest_django.asserts import assertRedirects
from django.contrib.auth import get_user_model


pytestmark = pytest.mark.django_db


User = get_user_model()

OK = HTTPStatus.OK
NOT_FOUND = HTTPStatus.NOT_FOUND

UNNAMED = pytest.lazy_fixture('client')
AUTHOR = pytest.lazy_fixture('author_client')
NOT_AUTHOR = pytest.lazy_fixture('not_author_client')
HOME = pytest.lazy_fixture('home_url')
DETAIL = pytest.lazy_fixture('detail_url')
LOGIN = pytest.lazy_fixture('login_url')
LOGOUT = pytest.lazy_fixture('logout_url')
SIGNUM = pytest.lazy_fixture('signup_url')
EDIT = pytest.lazy_fixture('edit_url')
DELETE = pytest.lazy_fixture('delete_url')
COMMENT_DELETE = pytest.lazy_fixture('comment_delete')
COMMENT_EDIT = pytest.lazy_fixture('comment_edit')


@pytest.mark.parametrize(
    'url, argument_client, expected_status',
    [
        (HOME, UNNAMED, OK),
        (DETAIL, UNNAMED, OK),
        (LOGIN, UNNAMED, OK),
        (LOGOUT, UNNAMED, OK),
        (SIGNUM, UNNAMED, OK),
        (EDIT, AUTHOR, OK),
        (DELETE, AUTHOR, OK),
        (EDIT, NOT_AUTHOR, NOT_FOUND),
        (DELETE, NOT_AUTHOR, NOT_FOUND),
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
        (COMMENT_DELETE),
        (COMMENT_EDIT),
    ),
)
def test_pages_redirects(client, name, login_url):
    """Редирект на страницу логина."""
    expected_url = f'{login_url}?next={name}'
    response = client.get(name)
    assertRedirects(response, expected_url)
