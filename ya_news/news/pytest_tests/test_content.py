from datetime import datetime, timedelta
import pytest

from django.test.client import Client
from django.contrib.auth import get_user_model
from django.utils.timezone import make_aware
from django.urls import reverse
from django.conf import settings

from news.models import Comment, News
from news.forms import CommentForm

User = get_user_model()


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def news():
    news = News.objects.create(
        title='Новость',
        text='Текст новости',
        date=datetime.today(),
    )
    return news


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def comment(author, news):
    comment = Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )
    return comment


@pytest.fixture
def news_pk(news):
    return news.id,


@pytest.fixture
def comment_data(author, news):
    now = make_aware(datetime.now())
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return news


@pytest.fixture
def count_news():
    today = datetime.today()
    all_news = []
    for index in range(settings.NEWS_COUNT_ON_HOME_PAGE):
        news = News(
            title=f'Новость {index}', text='Просто текст',
            date=today - timedelta(days=index)
        )
        all_news.append(news)
    News.objects.bulk_create(all_news)


@pytest.mark.django_db
def test_homepage_news_count(client, count_news):
    client.get(reverse('news:home'))
    news = News.objects.count()
    assert news == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_homepage_news_order(client, count_news):
    response = client.get(reverse('news:home'))
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, comment_data):
    response = client.get((reverse('news:detail', args=(comment_data.id,))))
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_created_dates = [comment.created for comment in all_comments]
    sorted_created_dates = sorted(all_created_dates)
    assert all_created_dates == sorted_created_dates


@pytest.mark.django_db
@pytest.mark.parametrize(
    'parametrized_client, expected_status',

    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False),
    ),
)
def test_different_client_has_form(parametrized_client,
                                   expected_status, news_pk):
    response = parametrized_client.get(reverse('news:detail', args=news_pk))
    form_in_context = 'form' in response.context
    assert form_in_context is expected_status
    if expected_status:
        form = response.context['form']
        assert isinstance(form, CommentForm)
