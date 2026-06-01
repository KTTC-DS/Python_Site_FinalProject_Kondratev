import pytest
from datetime import date, timedelta
from django.urls import reverse
from rentals.models import RentalRequest
from django.contrib.auth import get_user_model

User = get_user_model()

# ----- Тесты с фиксированными датами (2026–2027) -----

@pytest.mark.django_db
def test_create_rental_request_valid_dates(client, ad):
    """Создание запроса с корректными датами (арендатор не автор)"""
    renter = User.objects.create_user(username='renter', password='renterpass')
    client.login(username='renter', password='renterpass')
    response = client.post(reverse('create_rental_request', args=[ad.pk]), {
        'start_date': '2027-06-01',
        'end_date': '2027-06-05',
        'quantity': 2,
        'comment': 'Нужно к мероприятию'
    })
    assert response.status_code == 302
    assert RentalRequest.objects.filter(renter=renter, ad=ad).exists()
    req = RentalRequest.objects.first()
    assert req.status == 'pending'


@pytest.mark.django_db
def test_author_cannot_rent_own_ad(client, ad, user):
    """Автор не может арендовать своё объявление"""
    client.login(username='testuser', password='testpass123')
    response = client.post(reverse('create_rental_request', args=[ad.pk]), {
        'start_date': '2027-06-01',
        'end_date': '2027-06-05',
        'quantity': 1,
    }, follow=True)
    assert response.status_code == 200
    assert 'Вы не можете арендовать собственное объявление' in response.content.decode()
    assert not RentalRequest.objects.exists()


@pytest.mark.django_db
def test_rental_request_date_outside_range(client, ad):
    """Запрос не создаётся, если даты вне доступного диапазона"""
    # Убеждаемся, что диапазон объявления – 2027 год
    ad.available_from = date(2027, 1, 1)
    ad.available_until = date(2027, 12, 31)
    ad.save()

    renter = User.objects.create_user(username='renter2', password='pass')
    client.login(username='renter2', password='pass')
    response = client.post(reverse('create_rental_request', args=[ad.pk]), {
        'start_date': '2026-01-01',
        'end_date': '2026-01-05',
        'quantity': 1,
    })
    assert response.status_code == 200
    assert 'Аренда возможна только с' in response.content.decode()
    assert not RentalRequest.objects.exists()


@pytest.mark.django_db
def test_incoming_requests_view_for_owner(client, ad, user):
    """Владелец объявления видит входящие запросы"""
    renter = User.objects.create_user(username='renter', password='pass')
    RentalRequest.objects.create(
        ad=ad, renter=renter, start_date=date(2027, 6, 1), end_date=date(2027, 6, 5), quantity=1
    )
    client.login(username='testuser', password='testpass123')
    response = client.get(reverse('incoming_rental_requests'))
    assert response.status_code == 200
    assert 'renter' in response.content.decode()
    assert 'Тестовое объявление' in response.content.decode()


# ----- Тесты с динамическими датами (относительно сегодня) -----

@pytest.mark.django_db
def test_create_rental_request_dynamic_dates(client, ad):
    """Создание запроса с динамическими датами (через 30 дней от сегодня)"""
    renter = User.objects.create_user(username='dynamic_renter', password='pass')
    client.login(username='dynamic_renter', password='pass')

    # Устанавливаем доступный диапазон объявления, чтобы он включал наши динамические даты
    today = date.today()
    ad.available_from = today + timedelta(days=1)
    ad.available_until = today + timedelta(days=365)
    ad.save()

    start_date = today + timedelta(days=30)
    end_date = start_date + timedelta(days=5)

    response = client.post(reverse('create_rental_request', args=[ad.pk]), {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'quantity': 1,
        'comment': 'Динамическая дата'
    })
    assert response.status_code == 302
    assert RentalRequest.objects.filter(renter=renter, ad=ad).exists()
    req = RentalRequest.objects.first()
    assert req.start_date == start_date
    assert req.end_date == end_date


@pytest.mark.django_db
def test_rental_request_start_date_in_past(client, ad):
    """Запрос с датой начала в прошлом – должен быть отклонён"""
    renter = User.objects.create_user(username='past_user', password='pass')
    client.login(username='past_user', password='pass')

    # Делаем объявление доступным на широкий период, чтобы единственной ошибкой был "прошлый" старт
    today = date.today()
    ad.available_from = today - timedelta(days=30)
    ad.available_until = today + timedelta(days=365)
    ad.save()

    yesterday = today - timedelta(days=1)
    tomorrow = today + timedelta(days=1)

    response = client.post(reverse('create_rental_request', args=[ad.pk]), {
        'start_date': yesterday.isoformat(),
        'end_date': tomorrow.isoformat(),
        'quantity': 1,
    })
    assert response.status_code == 200
    assert 'Дата начала не может быть в прошлом' in response.content.decode()
    assert not RentalRequest.objects.exists()


@pytest.mark.django_db
def test_rental_request_end_date_before_start_date(client, ad):
    """Запрос с датой окончания раньше даты начала"""
    renter = User.objects.create_user(username='bad_dates_user', password='pass')
    client.login(username='bad_dates_user', password='pass')

    today = date.today()
    # Расширяем доступный диапазон, чтобы проверялась только ошибка порядка дат
    ad.available_from = today + timedelta(days=1)
    ad.available_until = today + timedelta(days=365)
    ad.save()

    start_date = today + timedelta(days=10)
    end_date = start_date - timedelta(days=5)  # end < start

    response = client.post(reverse('create_rental_request', args=[ad.pk]), {
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'quantity': 1,
    })
    assert response.status_code == 200
    assert 'Дата окончания не может быть раньше даты начала' in response.content.decode()
    assert not RentalRequest.objects.exists()
