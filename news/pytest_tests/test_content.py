    # ++ Количество новостей на главной странице — не более 10.
    # ++ Новости отсортированы от самой свежей к самой старой. Свежие новости в начале списка.
    # ++ Комментарии на странице отдельной новости отсортированы в хронологическом порядке: старые в начале списка, новые — в конце.
    # ++ Анонимному пользователю недоступна форма для отправки комментария на странице отдельной новости, а авторизованному доступна.
from django.conf import settings
from django.urls import reverse
import pytest
from news.models import News


HOME_URL = reverse('news:home')


def test_news_count(client, news_array):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE, "Убедитесь, что количество новостей на главной странице не более 10."


def test_news_order(client):
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates, "Убедитесь, что новости отсортированы от свежей к старой; свежие новости должны быть в начале списка."


def test_comments_order(client, news_object, comments_array):
    response = client.get(reverse('news:detail', args=(news_object.pk,)))
    assert 'news' in response.context, "Убедитесь, что на страницу новости действитеьно передается модель новости"
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created, "Убедитесь, что комментарии на странице отдельной новости отсортированы в хронологическом порядке: старые в начале списка, новые — в конце."


def test_anonymous_client_has_no_form(client, news_object):
    url = reverse('news:detail', args=(news_object.pk,))
    response = client.get(url)
    assert 'form' not in response.context, "Убедитесь, что анонимному пользователю недоступна форма для отправки комментария на странице отдельной новости."


def test_authorized_client_has_no_form(admin_client, news_object):
    url = reverse('news:detail', args=(news_object.pk,))
    response = admin_client.get(url)
    assert 'form' in response.context, "Убедитесь, что авторизованному пользователю доступна форма для отправки комментария на странице отдельной новости."