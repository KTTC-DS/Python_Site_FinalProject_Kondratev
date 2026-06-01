from django import forms
from .models import RentalRequest
from django.utils import timezone
from ads.models import Ad  # чтобы получить доступ к доступным датам


class RentalRequestForm(forms.ModelForm):
    class Meta:
        model = RentalRequest
        fields = ['start_date', 'end_date', 'quantity', 'comment']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'start_date': 'Дата начала',
            'end_date': 'Дата окончания',
            'quantity': 'Количество предметов',
            'comment': 'Комментарий',
        }

    def __init__(self, *args, **kwargs):
        # Принимаем дополнительный параметр ad для проверок
        self.ad = kwargs.pop('ad', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        ad = self.ad

        if not start_date or not end_date:
            return cleaned_data  # другие поля могут быть обязательными, но не проверяем

        # 1. Дата начала не в прошлом
        if start_date < timezone.now().date():
            self.add_error('start_date', 'Дата начала не может быть в прошлом.')

        # 2. Дата окончания не раньше даты начала
        if end_date < start_date:
            self.add_error('end_date', 'Дата окончания не может быть раньше даты начала.')

        # 3. Проверка доступности по полям объявления (если есть ad)
        if ad:
            if ad.available_from and start_date < ad.available_from:
                self.add_error('start_date', f'Аренда возможна только с {ad.available_from.strftime("%d.%m.%Y")}.')
            if ad.available_until and end_date > ad.available_until:
                self.add_error('end_date', f'Аренда возможна только до {ad.available_until.strftime("%d.%m.%Y")}.')

        return cleaned_data