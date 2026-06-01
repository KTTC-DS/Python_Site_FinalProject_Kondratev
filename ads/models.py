from django.db import models
from django.conf import settings


class Category(models.Model):
    """Категория одежды (например, Платья, Костюмы, Обувь)"""
    name = models.CharField('Название', max_length=100)
    slug = models.SlugField('URL', unique=True)
    description = models.TextField('Описание', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ad(models.Model):
    """Объявление об аренде одежды"""
    title = models.CharField('Заголовок', max_length=200)
    description = models.TextField('Описание')
    price_per_day = models.DecimalField('Цена за день (₽)', max_digits=10, decimal_places=2)
    location = models.CharField('Местоположение (город)', max_length=100)
    phone = models.CharField('Телефон', max_length=20, blank=True, help_text='Формат: +7 (123) 456-78-90')
    email = models.EmailField('Email', blank=True, help_text='example@mail.ru')
    image = models.ImageField('Фото', upload_to='ads/', blank=True, null=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)
    is_approved = models.BooleanField('Одобрено модератором', default=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='ads')
    categories = models.ManyToManyField(Category, verbose_name='Категории', blank=True, related_name='ads')
    available_from = models.DateField('Доступно с', null=True, blank=True)
    available_until = models.DateField('Доступно до', null=True, blank=True)

    class Meta:
        verbose_name = 'Объявление'
        verbose_name_plural = 'Объявления'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
