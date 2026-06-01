import pytest
from django.urls import reverse
from reviews.models import Review
from reviews.forms import ReviewForm
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_add_review_creates_review(client, ad, user):
    """Авторизованный пользователь может оставить отзыв"""
    client.login(username='testuser', password='testpass123')
    response = client.post(reverse('add_review', args=[ad.pk]), {
        'text': 'Отличная вещь!',
        'rating': 5
    })
    assert response.status_code == 302
    assert Review.objects.filter(ad=ad, author=user).exists()

@pytest.mark.django_db
def test_add_review_only_one_per_user(client, ad, user):
    """Пользователь не может оставить более одного отзыва на одно объявление"""
    client.login(username='testuser', password='testpass123')
    client.post(reverse('add_review', args=[ad.pk]), {'text': 'Хорошо', 'rating': 4})
    response = client.post(reverse('add_review', args=[ad.pk]),
                           {'text': 'Повтор', 'rating': 5},
                           follow=True)
    assert response.status_code == 200
    assert 'Вы уже оставляли отзыв' in response.content.decode()
    assert Review.objects.filter(ad=ad, author=user).count() == 1

@pytest.mark.django_db
def test_review_str_method(ad, user):
    """Строковое представление отзыва"""
    review = Review.objects.create(ad=ad, author=user, text='Отлично!', rating=5)
    expected = f'Отзыв от {user.username} на {ad.title}'
    assert str(review) == expected

@pytest.mark.django_db
def test_add_review_with_photo(client, ad, user, test_image):
    """Отзыв с фотографией"""
    client.login(username='testuser', password='testpass123')
    response = client.post(reverse('add_review', args=[ad.pk]), {
        'text': 'Отличная вещь!',
        'rating': 5,
        'image': test_image
    })
    assert response.status_code == 302
    review = Review.objects.first()
    assert review.image.name.startswith('review_photos/test')
    assert review.text == 'Отличная вещь!'

@pytest.mark.django_db
def test_review_photo_display_in_ad_detail(client, ad, user, test_image):
    """Фото отображается на странице объявления"""
    client.login(username='testuser', password='testpass123')
    client.post(reverse('add_review', args=[ad.pk]), {
        'text': 'Супер',
        'rating': 4,
        'image': test_image
    })
    response = client.get(reverse('ad_detail', args=[ad.pk]))
    content = response.content.decode()
    assert 'Супер' in content
    assert 'test.png' in content or 'review_photos/test' in content

@pytest.mark.django_db
def test_review_form_with_image(test_image):
    """Форма принимает изображение"""
    form = ReviewForm(data={'text': 'Nice', 'rating': 3}, files={'image': test_image})
    assert form.is_valid()

# ----- Тесты пагинации отзывов (исправленные) -----

@pytest.mark.django_db
def test_review_pagination(client, ad):
    """Проверка пагинации отзывов (5 на страницу) – считаем количество карточек"""
    # Создаём 7 отзывов от разных пользователей
    for i in range(7):
        username = f'reviewer{i}'
        user = User.objects.create_user(username=username, password='pass')
        Review.objects.create(
            ad=ad,
            author=user,
            text=f'Отзыв номер {i+1}',
            rating=5
        )

    # Первая страница (без параметра reviews_page)
    response = client.get(reverse('ad_detail', args=[ad.pk]))
    assert response.status_code == 200
    content = response.content.decode()

    # Считаем количество карточек отзывов (по классу card mb-2)
    review_cards_count = content.count('<div class="card mb-2">')
    assert review_cards_count == 5, f"На первой странице должно быть 5 отзывов, найдено {review_cards_count}"

    # Вторая страница
    response = client.get(reverse('ad_detail', args=[ad.pk]), {'reviews_page': 2})
    content = response.content.decode()
    review_cards_count = content.count('<div class="card mb-2">')
    assert review_cards_count == 2, f"На второй странице должно быть 2 отзыва, найдено {review_cards_count}"

@pytest.mark.django_db
def test_empty_reviews_no_pagination(client, ad):
    """Если отзывов нет, пагинация не отображается"""
    response = client.get(reverse('ad_detail', args=[ad.pk]))
    assert response.status_code == 200
    assert 'Пока нет отзывов' in response.content.decode()
    # Проверяем, что нет ссылок с параметром reviews_page
    assert 'reviews_page=' not in response.content.decode()
