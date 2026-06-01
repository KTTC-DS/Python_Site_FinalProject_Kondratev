from django import forms
from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text', 'rating', 'image']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3}),
            'image': forms.ClearableFileInput(attrs={'accept': 'image/*'}),
        }
        labels = {
            'text': 'Текст отзыва',
            'rating': 'Оценка (1-5)',
            'image': 'Фотография (необязательно)',
        }