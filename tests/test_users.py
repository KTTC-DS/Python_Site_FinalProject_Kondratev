import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from users.forms import RegistrationForm

User = get_user_model()

@pytest.mark.django_db
def test_user_creation():
    """Создание пользователя через модель"""
    user = User.objects.create_user(username='testuser', email='test@ex.com', password='pass')
    assert user.username == 'testuser'
    assert user.check_password('pass')

@pytest.mark.django_db
def test_registration_form_valid():
    """Форма регистрации принимает корректные данные"""
    form = RegistrationForm(data={
        'username': 'newuser',
        'email': 'new@ex.com',
        'password1': 'strongpass123',
        'password2': 'strongpass123'
    })
    assert form.is_valid()

@pytest.mark.django_db
def test_registration_form_password_mismatch():
    """Форма регистрации не принимает несовпадающие пароли"""
    form = RegistrationForm(data={
        'username': 'newuser',
        'email': 'new@ex.com',
        'password1': 'pass123',
        'password2': 'pass456'
    })
    assert not form.is_valid()
    assert 'password2' in form.errors

@pytest.mark.django_db
def test_register_view_post_valid(client):
    """POST-запрос на регистрацию создаёт пользователя и редиректит"""
    response = client.post(reverse('register'), data={
        'username': 'reguser',
        'email': 'reg@ex.com',
        'password1': 'testpass123',
        'password2': 'testpass123'
    })
    assert response.status_code == 302
    assert User.objects.filter(username='reguser').exists()