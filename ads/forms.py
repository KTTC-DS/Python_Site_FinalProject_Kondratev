from django import forms
from .models import Ad
import re


class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['title',
                  'description',
                  'categories',
                  'price_per_day',
                  'location',
                  'phone',
                  'email',
                  'image',
                  'available_from',
                  'available_until',
                 ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'phone': forms.TextInput(attrs={
                'placeholder': '+7 (123) 456-78-90',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'example@mail.ru',
                'class': 'form-control'
            }),
            'available_from': forms.DateInput(attrs={'type': 'date'}),
            'available_until': forms.DateInput(attrs={'type': 'date'}),
            'categories': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 5}),
        }
        labels = {
            'phone': 'Номер телефона',
            'email': 'Электронная почта',
            'available_from': 'Доступно с',
            'available_until': 'Доступно до',
            'categories': 'Категории (можно выбрать несколько)',
        }
        help_texts = {
            'phone': 'Введите номер в формате +7 (123) 456-78-90',
            'email': 'Введите адрес электронной почты',
        }

    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get('phone')
        email = cleaned_data.get('email')
        if not phone and not email:
            self.add_error(None, 'Укажите хотя бы один способ связи: телефон или email.')
        return cleaned_data

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            phone_pattern = re.compile(r'^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$')
            if not phone_pattern.match(phone):
                raise forms.ValidationError(
                    'Номер телефона должен быть в формате +7 (123) 456-78-90.'
                )
        return phone
