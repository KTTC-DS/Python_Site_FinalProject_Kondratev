import pytest
import base64
from datetime import date
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from ads.models import Ad, Category

User = get_user_model()

@pytest.fixture
def user():
    """Обычный пользователь"""
    return User.objects.create_user(username='testuser', password='testpass123')

@pytest.fixture
def staff_user():
    """Пользователь с правами персонала (админ)"""
    return User.objects.create_user(username='admin', password='adminpass', is_staff=True)

@pytest.fixture
def category():
    """Категория для тестов"""
    return Category.objects.create(name='Тестовая категория', slug='test-cat')

@pytest.fixture
def ad(user):
    """Одобренное объявление с доступными датами в будущем (2027 год)"""
    return Ad.objects.create(
        title='Тестовое объявление',
        description='Описание для теста',
        price_per_day=100,
        location='Москва',
        phone='+7 (123) 456-78-90',
        email='test@example.com',
        author=user,
        is_approved=True,
        available_from=date(2027, 1, 1),
        available_until=date(2027, 12, 31)
    )

@pytest.fixture
def test_image():
    """Фикстура: настоящее PNG-изображение (1×1 пиксель) для тестов"""
    png_base64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=='
    return SimpleUploadedFile(
        name='test.png',
        content=base64.b64decode(png_base64),
        content_type='image/png'
    )
