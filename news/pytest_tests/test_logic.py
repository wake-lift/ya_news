    # ++ Анонимный пользователь не может отправить комментарий.
    # ++ Авторизованный пользователь может отправить комментарий.
    # Если комментарий содержит запрещённые слова, он не будет опубликован, а форма вернёт ошибку.
    # ++ Авторизованный пользователь может редактировать или удалять свои комментарии.
    # ++ Авторизованный пользователь не может редактировать или удалять чужие комментарии.
from http import HTTPStatus
from pytest_django.asserts import assertFormError, assertRedirects

from django.urls import reverse
from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News




def test_anonymous_user_cant_create_comment(client, news_object, form_data):
    url = reverse('news:detail', args=(news_object.pk,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url, msg_prefix="Убедитесь, что при попытке создать комментарий анонимный пользователь перенаправляется на страницу логина.")
    assert Comment.objects.count() == 0, "Убедитесь, что анонимный пользователь не может создать комментарий."


def test_authorized_user_can_create_comment(news_object, author_comment, author_comment_client, form_data):
    url = reverse('news:detail', args=(news_object.pk,))
    response = author_comment_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments', msg_prefix="Убедитесь, после создания комментария пользователь перенаправляется в раздел комментариев на странице новости.")
    comments_count = Comment.objects.count()
    assert comments_count == 1, "Убедитесь, что аутентифицированный пользователь может создать комментарий."
    new_comment = Comment.objects.get()
    assert new_comment.news == news_object, "Убедитесь, что созданный комментарий действительно относится к соответствующей новости."
    assert new_comment.text == form_data['text'], "Убедитесь, что созданный комментарий действительно содержит тот же текст, что и в форме."
    assert new_comment.author == author_comment, "Убедитесь, что созданный комментарий действительно принадлежит залогиненному пользователю."


def test_user_cant_use_bad_words(admin_client, news_object):
    bad_words_data = {'text': f'.... {BAD_WORDS[0]} ....'}
    url = reverse('news:detail', args=(news_object.pk,))
    response = admin_client.post(url, data=bad_words_data)
    assertFormError(response, form='form', field='text', errors=WARNING, msg_prefix="Убедитесь, что если комментарий содержит запрещённые слова, форма вернёт ошибку.")
    comments_count = Comment.objects.count()
    assert comments_count == 0, "Убедитесь, что если комментарий содержит запрещённые слова, он не будет опубликован."


def test_author_can_edit_comment(news_object, comment_object, author_comment_client, form_data):
    url = reverse('news:edit', args=(comment_object.pk,))
    response = author_comment_client.post(url, form_data)
    assertRedirects(response, reverse('news:detail', args=(news_object.pk,)) + '#comments', msg_prefix="Убедитесь, после редактирования комментария пользователь перенаправляется в раздел комментариев на странице новости.")
    comment_object.refresh_from_db()
    assert comment_object.text == form_data['text'], "Убедитесь, что отредактированный комментарий действительно содержит тот же текст, что и в форме."


def test_other_user_cant_edit_comment(comment_object, admin_client, form_data):
    url = reverse('news:edit', args=(comment_object.pk,))
    response = admin_client.post(url, form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND, "Убедитесь, что страница редактирования комментария доступна только его автору."
    comment_from_db = Comment.objects.get(pk=comment_object.pk)
    assert comment_from_db.text == comment_object.text, "Убедитесь, что редактировать комментарий может только его автор."


def test_author_can_delete_comment(news_object, comment_object, author_comment_client):
    url = reverse('news:delete', args=(comment_object.pk,))
    response = author_comment_client.post(url)
    assertRedirects(response, reverse('news:detail', args=(news_object.pk,)) + '#comments', msg_prefix="Убедитесь, после удаления комментария пользователь перенаправляется в раздел комментариев на странице новости.")
    assert Comment.objects.count() == 0, "Убедитесь, что после удаления комментария он действительно исчезает из базы данных."


def test_other_user_cant_delete_comment(admin_client, comment_object):
    url = reverse('news:delete', args=(comment_object.pk,))
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND, "Убедитесь, что страница удаления комментария доступна только его автору."
    assert Comment.objects.count() == 1, "Убедитесь, что удалить комментарий может только его автор."
