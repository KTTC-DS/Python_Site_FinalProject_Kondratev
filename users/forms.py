from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User



class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=20, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'phone', 'password1', 'password2')
        labels = {
        'username': 'Имя пользователя',
        'password1': 'Пароль',
        'password2': 'Подтверждение пароля',
        }
        help_texts = {
        'username': 'Обязательное поле. Не более 150 символов. Только буквы, цифры и @/./+/-/_.',
        'password1': 'Пароль должен содержать не менее 8 символов и не быть слишком простым.',
        }
