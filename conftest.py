from datetime import datetime, timedelta
import pytest
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
from news.models import News, Comment


@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """Фикстура, позволяющая получать доступ к базе данных без маркера django_db."""
    pass


@pytest.fixture
def author_comment(django_user_model):
    """Фикстура, создающая автора комментария."""
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_comment_client(author_comment, client):
    """Фикстура, создающая клиент, авторизованный для автора комментария."""
    client.force_login(author_comment)
    return client


@pytest.fixture
def news_object():
    """Фикстура, создающая объект новости."""
    news = News.objects.create(
        title='Заголовок новости',
        text='Текст новости',
    )
    return news


@pytest.fixture
def comment_object(author_comment, news_object):
    """Фикстура, создающая объект комментария."""
    comment = Comment.objects.create(
        news=news_object,
        author=author_comment,
        text='Текст комментария',
    )
    return comment


@pytest.fixture
def news_array():
    """Фикстура, создающая объекты новостей в количестве, превышающем вывод на страницу, с разным временем создания."""
    today = datetime.today()
    News.objects.bulk_create(
        News(title=f'Новость {index}', text='Текст новости {index}.', date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    )


@pytest.fixture
def comments_array(news_object, author_comment):
    """Фикстура, создающая два объекта комментария к новости с различным временем создания."""
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
                news=news_object, author=author_comment, text=f'Tекст комментария № {index}.',
            )
        comment.created = now + timedelta(days=index)
        comment.save()


@pytest.fixture
def form_data():
    return {
        'text': 'Комментарий для формы',
    }
