from random import choice
from http import HTTPStatus

import pytest
from pytest_django.asserts import assertFormError, assertRedirects
from django.contrib.auth import get_user_model
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING


pytestmark = pytest.mark.django_db

User = get_user_model()


def test_anonymous_cant_sent_comment(client, detail_url, comment_data):
    result = Comment.objects.count()
    client.post((detail_url), data=comment_data)
    assert Comment.objects.count() == result


def test_user_can_sent_comment(author_client, news, detail_url, author, comment_data):
    Comment.objects.all().delete()
    author_client.post((detail_url), data=comment_data
    )
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == comment_data['text']
    assert comment.author == author
    assert comment.news == news


def test_user_cant_use_bad_words(author_client, news, detail_url, comment_data):
    result = Comment.objects.count()
    comment_data['text'] = f'text, {choice(BAD_WORDS)}.'
    response = author_client.post((detail_url), data=comment_data
    )
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == result


def test_author_can_edit_comment(author_client, comment, author, news, detail_url, edit_url, comment_data):
    result = Comment.objects.count()
    url_to_comments = f'{detail_url}#comments'
    response = author_client.post(edit_url, data=comment_data
    )
    assertRedirects(response, url_to_comments)
    assert Comment.objects.count() == result
    comment = Comment.objects.get(id=comment.id)
    assert comment.text == comment_data['text']
    assert comment.author == author
    assert comment.news == news


def test_another_user_cant_edit_comment(admin_client, comment, edit_url, comment_data):
    result = Comment.objects.count()
    response = admin_client.post(edit_url, data=comment_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == result
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author
    assert comment.news == comment_from_db.news


def test_author_can_delete_comment(author_client, comment, author, detail_url, delete_url):
    url_comments = f'{detail_url}#comments'
    result = Comment.objects.count()
    response = author_client.delete(delete_url)
    assertRedirects(response, url_comments)
    assert Comment.objects.count() == result - 1


def test_another_user_cant_delete_comment(admin_client, comment, delete_url):
    result = Comment.objects.count()
    response = admin_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == result
