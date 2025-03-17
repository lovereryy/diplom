from django import forms
from .models import Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["score", "text"]

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email"]  # Только имя и почта
        labels = {
            "username": "Имя",
            "email": "Email",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        # Автоматически заполняем поля текущими данными пользователя
        self.fields["username"].initial = self.instance.username
        self.fields["email"].initial = self.instance.email

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'})
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        label="Имя пользователя",
        help_text="Введите уникальное имя пользователя (буквы, цифры, @/./+/-/_).",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ваше имя'})
    )
    password1 = forms.CharField(
        label="Пароль",
        help_text="Пароль должен содержать минимум 8 символов.",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Придумайте пароль'})
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        help_text="Введите пароль ещё раз для подтверждения.",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'})
    )

    class Meta:
        model = User
        fields = ("username", "password1", "password2")