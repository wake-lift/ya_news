    # ++ Главная страница доступна анонимному пользователю.
    # ++ Страница отдельной новости доступна анонимному пользователю.
    # ++ Страницы удаления и редактирования комментария доступны автору комментария.
    # ++ При попытке перейти на страницу редактирования или удаления комментария анонимный пользователь перенаправляется на страницу авторизации.
    # ++ Авторизованный пользователь не может зайти на страницы редактирования или удаления чужих комментариев (возвращается ошибка 404).
    # ++ Страницы регистрации пользователей, входа в учётную запись и выхода из неё доступны анонимным пользователям.

from http import HTTPStatus

from django.urls import reverse
import pytest
from pytest_django.asserts import assertRedirects


@pytest.mark.parametrize(
    'name, args, msg', (
        ('news:home', None, 'Убедитесь, что главная страница доступна анонимному пользователю.',),
        ('users:login', None, 'Убедитесь, что страница входа в учётную запись доступна анонимному пользователю.',),
        ('users:logout', None, 'Убедитесь, что страница выхода из учётной записи доступна анонимному пользователю.',),
        ('users:signup', None, 'Убедитесь, что страница регистрации пользователей доступна анонимному пользователю.',),
        ('news:detail', True, 'Убедитесь, что страница отдельной новости доступна анонимному пользователю.',),
    )
)
def test_pages_availability_for_anonymous_user(client, news_object, name, args, msg):
    if args:
        args = (news_object.pk,)
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK, msg


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
        (pytest.lazy_fixture('author_comment_client'), HTTPStatus.OK)
    ),
)
@pytest.mark.parametrize(
    'name, msg', (
        ('news:delete', 'Убедитесь, что страница удаления комментария доступна автору комментария, а авторизованный пользователь не может зайти на страницу удаления чужого комментария.',),
        ('news:edit', 'Убедитесь, что страница редактировавния комментария доступна автору комментария, а авторизованный пользователь не может зайти на страницу редактирования чужого комментария.',),
    )
)
def test_pages_availability_for_different_users(
        parametrized_client, comment_object, name, expected_status, msg
):
    url = reverse(name, args=(comment_object.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status, msg


@pytest.mark.parametrize(
    'name, msg', (
        ('news:delete', 'Убедитесь, что при попытке перейти на страницу удаления комментария анонимный пользователь перенаправляется на страницу авторизации.',),
        ('news:edit', 'Убедитесь, что при попытке перейти на страницу редактирования комментария анонимный пользователь перенаправляется на страницу авторизации.',),
    )
)
def test_redirects(client, comment_object, name, msg):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment_object.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url, msg_prefix=msg)
