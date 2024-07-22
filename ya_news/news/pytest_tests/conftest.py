from datetime import datetime, timedelta

import pytest
from django.test.client import Client
from django.utils.timezone import make_aware
from django.urls import reverse
from django.conf import settings

from news.models import Comment, News


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



@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')



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
def home_url():
    return reverse('news:home')

@pytest.fixture
def detail_url(news):
    return reverse('news:detail', args=(news.id,))

@pytest.fixture
def edit_url(comment):
    return reverse('news:edit', args=(comment.id,))


@pytest.fixture
def delete_url(comment):
    return reverse('news:delete', args=(comment.id,))

@pytest.fixture
def login_url():
    return reverse('users:login')


@pytest.fixture
def logout_url():
    return reverse('users:logout')


@pytest.fixture
def signup_url():
    return reverse('users:signup')

@pytest.fixture
def comment_data():
    return {'text': 'Текст.'}
