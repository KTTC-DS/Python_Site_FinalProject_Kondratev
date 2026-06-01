from django.db import models
from django.conf import settings
from ads.models import Ad



class Review(models.Model):
    """Отзыв на объявление"""
    ad = models.ForeignKey(Ad, on_delete=models.CASCADE, related_name='reviews')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField('Текст отзыва')
    rating = models.PositiveSmallIntegerField('Оценка (1-5)', choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField('Фото', upload_to='review_photos/', blank=True, null=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('ad', 'author')   # один пользователь — один отзыв на объявление

    def __str__(self):
        return f'Отзыв от {self.author.username} на {self.ad.title}'

class ReviewPhoto(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField('Фото', upload_to='review_photos/')
    created_at = models.DateTimeField(auto_now_add=True)