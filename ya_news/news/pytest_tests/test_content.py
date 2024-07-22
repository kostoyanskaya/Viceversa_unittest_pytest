import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings

from news.models import News
from news.forms import CommentForm


pytestmark = pytest.mark.django_db


User = get_user_model()


def test_homepage_news_count(client, count_news, home_url):
    client.get(home_url)
    news = News.objects.count()
    assert news == settings.NEWS_COUNT_ON_HOME_PAGE


def test_homepage_news_order(client, count_news, home_url):
    response = client.get(home_url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, detail_url):
    response = client.get(detail_url)
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_created_dates = [comment.created for comment in all_comments]
    sorted_created_dates = sorted(all_created_dates)
    assert all_created_dates == sorted_created_dates


@pytest.mark.parametrize(
    'parametrized_client, expected_status',

    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    ),
)
def test_different_client_has_form(parametrized_client,
                                   expected_status, detail_url):
    response = parametrized_client.get(detail_url)
    form_in_context = 'form' in response.context
    assert form_in_context is expected_status
    if expected_status:
        form = response.context['form']
        assert isinstance(form, CommentForm)
