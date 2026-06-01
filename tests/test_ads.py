import pytest
from django.urls import reverse
from ads.models import Ad, Category
from ads.forms import AdForm
from django.contrib.auth import get_user_model

User = get_user_model()

@pytest.mark.django_db
def test_ad_creation(user):
    """Создание объявления через модель"""
    ad = Ad.objects.create(
        title='Моё объявление',
        description='Описание',
        price_per_day=200,
        location='СПб',
        phone='+7 (999) 111-22-33',
        email='a@a.com',
        author=user,
        is_approved=False
    )
    assert ad.title == 'Моё объявление'
    assert not ad.is_approved

@pytest.mark.django_db
def test_ad_form_valid():
    """Форма объявления принимает корректные данные"""
    form = AdForm(data={
        'title': 'Форма объявления',
        'description': 'Описание',
        'price_per_day': 150,
        'location': 'Казань',
        'phone': '+7 (123) 456-78-90',
        'email': 'form@ex.com'
    })
    assert form.is_valid()

@pytest.mark.django_db
def test_ad_list_view_shows_only_approved(client, ad):
    """В списке объявлений отображаются только одобренные"""
    Ad.objects.create(
        title='Скрытое объявление',
        description='Не одобрено',
        price_per_day=10,
        location='Москва',
        phone='+7 (111) 111-11-11',
        email='hidden@ex.com',
        author=ad.author,
        is_approved=False
    )
    response = client.get(reverse('ad_list'))
    content = response.content.decode()
    assert 'Тестовое объявление' in content
    assert 'Скрытое объявление' not in content

@pytest.mark.django_db
def test_ad_search_by_keyword(client, ad):
    """Поиск объявлений по ключевому слову"""
    response = client.get(reverse('ad_list'), {'q': 'Тестовое'})
    assert 'Тестовое объявление' in response.content.decode()
    response2 = client.get(reverse('ad_list'), {'q': 'Нет такого'})
    assert 'Тестовое объявление' not in response2.content.decode()

@pytest.mark.django_db
def test_ad_detail_contacts_hidden_for_anonymous(client, ad):
    """Контакты скрыты для неавторизованных"""
    response = client.get(reverse('ad_detail', args=[ad.pk]))
    content = response.content.decode()
    assert 'test@example.com' not in content
    assert 'Войдите' in content

@pytest.mark.django_db
def test_ad_detail_contacts_visible_for_authorized(client, ad, user):
    """Авторизованный пользователь видит контакты"""
    client.login(username='testuser', password='testpass123')
    response = client.get(reverse('ad_detail', args=[ad.pk]))
    assert 'test@example.com' in response.content.decode()

@pytest.mark.django_db
def test_ad_moderation_access_denied_for_regular_user(client, user):
    """Обычный пользователь не может зайти на модерацию"""
    client.login(username='testuser', password='testpass123')
    response = client.get(reverse('ad_moderation'))
    assert response.status_code == 302
    assert response.url.startswith('/admin/login/')

@pytest.mark.django_db
def test_ad_moderation_access_allowed_for_staff(client, staff_user):
    """Сотрудник может зайти на модерацию"""
    client.login(username='admin', password='adminpass')
    response = client.get(reverse('ad_moderation'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_ad_moderation_approve(client, staff_user, user):
    """Модератор может одобрить объявление"""
    pending_ad = Ad.objects.create(
        title='Pending Ad',
        description='Needs approval',
        price_per_day=50,
        location='Moscow',
        phone='+7 (999) 111-22-33',
        email='pending@ex.com',
        author=user,
        is_approved=False
    )
    client.login(username='admin', password='adminpass')
    response = client.post(reverse('ad_moderation'), {f'approve_{pending_ad.id}': 'approve'})
    assert response.status_code == 302
    pending_ad.refresh_from_db()
    assert pending_ad.is_approved

@pytest.mark.django_db
def test_ad_moderation_delete(client, staff_user, user):
    """Модератор может удалить объявление"""
    pending_ad = Ad.objects.create(
        title='To Delete',
        description='Will be deleted',
        price_per_day=30,
        location='SPb',
        phone='+7 (999) 333-44-55',
        email='delete@ex.com',
        author=user,
        is_approved=False
    )
    client.login(username='admin', password='adminpass')
    response = client.post(reverse('ad_moderation'), {f'approve_{pending_ad.id}': 'delete'})
    assert response.status_code == 302
    assert not Ad.objects.filter(pk=pending_ad.pk).exists()

@pytest.mark.django_db
def test_my_ads_shows_only_users_ads(client, user):
    """В 'Моих объявлениях' отображаются только объявления текущего пользователя"""
    client.login(username='testuser', password='testpass123')
    Ad.objects.create(
        title='User Ad',
        description='My ad',
        price_per_day=100,
        location='Kazan',
        phone='+7 (123) 456-78-90',
        email='user@ex.com',
        author=user,
        is_approved=True
    )
    other_user = User.objects.create_user(username='other', password='other')
    Ad.objects.create(
        title='Other Ad',
        description='Not mine',
        price_per_day=200,
        location='Moscow',
        phone='+7 (999) 888-77-66',
        email='other@ex.com',
        author=other_user,
        is_approved=True
    )
    response = client.get(reverse('my_ads'))
    content = response.content.decode()
    assert 'User Ad' in content
    assert 'Other Ad' not in content

@pytest.mark.django_db
def test_ad_list_filter_by_category(client, ad, category):
    """Фильтрация по категории"""
    ad.categories.add(category)
    ad.save()
    other_ad = Ad.objects.create(
        title='Other Ad',
        description='Different category',
        price_per_day=150,
        location='SPb',
        phone='+7 (111) 222-33-44',
        email='other@ex.com',
        author=ad.author,
        is_approved=True
    )
    response = client.get(reverse('ad_list'), {'category': category.slug})
    content = response.content.decode()
    assert ad.title in content
    assert other_ad.title not in content

@pytest.mark.django_db
def test_moderation_page_shows_full_ad_details(client, staff_user):
    """Админ видит полную информацию об объявлении на странице модерации"""
    client.login(username='admin', password='adminpass')
    cat = Category.objects.create(name='Test Cat', slug='test-cat')
    ad = Ad.objects.create(
        title='Full Ad',
        description='Full description',
        price_per_day=999,
        location='Test City',
        phone='+7 (123) 456-78-90',
        email='test@example.com',
        author=staff_user,
        is_approved=False,
        available_from='2025-01-01',
        available_until='2025-12-31'
    )
    ad.categories.add(cat)
    response = client.get(reverse('ad_moderation'))
    content = response.content.decode()
    assert 'Full Ad' in content
    assert 'Full description' in content
    assert '999' in content
    assert 'Test City' in content
    assert 'test@example.com' in content
    assert 'Test Cat' in content
