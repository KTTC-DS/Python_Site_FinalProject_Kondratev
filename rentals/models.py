from django.db import models
from django.conf import settings
from ads.models import Ad



class RentalRequest(models.Model):
    """Запрос на аренду от пользователя"""
    STATUS_CHOICES = (
        ('pending', 'На рассмотрении'),
        ('approved', 'Одобрен'),
        ('rejected', 'Отклонён'),
        ('cancelled', 'Отменён'),
    )
    ad = models.ForeignKey(
        Ad,
        on_delete=models.CASCADE,
        related_name='rental_requests',
        verbose_name='Объявление'
    )
    renter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='rental_requests',
        verbose_name='Арендатор'
    )
    start_date = models.DateField('Дата начала аренды')
    end_date = models.DateField('Дата окончания аренды')
    quantity = models.PositiveIntegerField('Количество предметов', default=1)
    comment = models.TextField('Комментарий', blank=True)
    status = models.CharField(
        'Статус',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлён', auto_now=True)

    class Meta:
        verbose_name = 'Запрос на аренду'
        verbose_name_plural = 'Запросы на аренду'
        ordering = ['-created_at']

    def __str__(self):
        return f'Запрос от {self.renter.username} на {self.ad.title}'



class Transaction(models.Model):
    """Транзакция по аренде (оплата)"""
    rental_request = models.OneToOneField(
        RentalRequest,
        on_delete=models.CASCADE,
        related_name='transaction',
        verbose_name='Запрос'
    )
    amount = models.DecimalField('Сумма', max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField('Дата платежа', auto_now_add=True)
    transaction_id = models.CharField(
        'ID транзакции',
        max_length=100,
        blank=True
        )
    is_paid = models.BooleanField('Оплачено', default=False)

    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    def __str__(self):
        return f'Транзакция {self.transaction_id or self.pk} на сумму {self.amount} ₽'
