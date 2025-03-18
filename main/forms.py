from django import forms
from .models import Review
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError


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
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'})
    )

class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        label="Имя",
        help_text="Введите ваше реальное имя.",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}),
    )
    email = forms.EmailField(
        label="Email",
        help_text="Введите действующий email-адрес.",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'}),
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
        fields = ("first_name", "email", "password1", "password2")

    def clean_email(self):
        """ Проверяем, что email уникальный """
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже используется.")
        return email