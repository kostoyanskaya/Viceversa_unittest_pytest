from datetime import datetime
import pytest
from random import choice

from pytest_django.asserts import assertFormError, assertRedirects
from django.test.client import Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from http import HTTPStatus

from news.models import Comment, News
from news.forms import BAD_WORDS, WARNING

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
def test_anonymous_cant_sent_comment(client, news_pk):
    result = Comment.objects.count()
    client.post(reverse('news:detail', args=news_pk), data={'text': 'Текст.'})
    assert Comment.objects.count() == result


@pytest.mark.django_db
def test_user_can_sent_comment(author_client, news_pk):
    result = Comment.objects.count() + 1
    author_client.post(reverse(
        'news:detail', args=news_pk), data={'text': 'Текст.'}
    )
    assert Comment.objects.count() == result


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news_pk):
    result = Comment.objects.count()
    form_data = {'text': 'Текст.'}
    form_data['text'] = f'text, {choice(BAD_WORDS)}.'
    response = author_client.post(reverse(
        'news:detail', args=news_pk), data=form_data
    )
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == result


@pytest.mark.django_db
def test_author_can_edit_comment(author_client, comment, author, news):
    url = reverse('news:detail', args=(news.id,))
    url_to_comments = f'{url}#comments'
    response = author_client.post(reverse(
        'news:edit', args=(comment.id,)), data={'text': 'Текст.'}
    )
    assertRedirects(response, url_to_comments)
    form_data = {'text': 'Текст.'}
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_another_user_cant_edit_comment(admin_client, comment):
    response = admin_client.post(reverse(
        'news:edit', args=(comment.id,)), data={'text': 'Текст.'}
    )
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment, author, news):
    url = reverse('news:detail', args=(news.id,))
    url_comments = f'{url}#comments'
    result = Comment.objects.count()
    response = author_client.delete(reverse('news:delete', args=(comment.id,)))
    assertRedirects(response, url_comments)
    assert Comment.objects.count() == result - 1


@pytest.mark.django_db
def test_another_user_cant_delete_comment(admin_client, comment):
    result = Comment.objects.count()
    response = admin_client.delete(reverse('news:delete', args=(comment.id,)))
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == result
