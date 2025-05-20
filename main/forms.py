from django import forms
from .models import Review, TableBooking
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from django.forms.widgets import DateInput, TimeInput
from django.forms import Select


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["score", "text"]

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["username", "email", "first_name"]
        labels = {
            "username": "Никнейм",
            "email": "Email",
            "first_name": "Имя",
        }
        widgets = {
            "username": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super(CustomUserChangeForm, self).__init__(*args, **kwargs)
        # Автоматически заполняем поля текущими данными пользователя
        self.fields["username"].initial = self.instance.username
        self.fields["email"].initial = self.instance.email
        self.fields["first_name"].initial = self.instance.first_name

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'}),
    )
    password = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введите пароль'}),
    )


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        label="Имя",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя'}),
    )
    username = forms.CharField(
        label="Имя пользователя",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите имя пользователя'}),
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'}),
    )
    password1 = forms.CharField(
        label="Пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Придумайте пароль'}),
    )
    password2 = forms.CharField(
        label="Подтверждение пароля",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Повторите пароль'}),
    )

    class Meta:
        model = User
        fields = ("first_name", "username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже используется.")
        return email


class TableBookingForm(forms.ModelForm):
    GUESTS_CHOICES = [(i, str(i)) for i in range(1, 9)]  # Список от 1 до 8
    
    guests_count = forms.ChoiceField(
        choices=GUESTS_CHOICES,
        widget=forms.Select(attrs={
            'disabled': 'disabled',  # по умолчанию отключено, как у тебя
            'class': 'form-control',
        }),
        label="Количество гостей"
    )

    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'phone',
            'placeholder': '+7 (___) ___-__-__',
        }),
        label="Телефон"
    )
    
    class Meta:
        model = TableBooking
        fields = ['table', 'booking_type', 'guests_count', 'date', 'time', 'phone']
        widgets = {
            'date': forms.TextInput(attrs={'placeholder': 'Укажите дату', 'disabled': 'disabled', 'id': 'id_date'}),
            'time': forms.Select(attrs={'placeholder': 'Выберите время', 'disabled': 'disabled', 'id': 'id_time'}),
            'table': forms.Select(attrs={'placeholder': 'Выберите столик', 'disabled': 'disabled'}),
            'booking_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        import re
        # Простейшая проверка: только цифры, плюс и длина
        digits = re.sub(r'\D', '', phone)
        if len(digits) < 11:
            raise forms.ValidationError("Введите корректный номер телефона")
        return phone

    def clean(self):
        cleaned_data = super().clean()
        # guests_count приходит как строка, надо превратить в int для проверки
        guests_count = cleaned_data.get("guests_count")
        if guests_count is not None:
            cleaned_data["guests_count"] = int(guests_count)

        # Остальная логика проверки гостей как у тебя
        table = cleaned_data.get("table")
        booking_type = cleaned_data.get("booking_type")
        guests_count = cleaned_data.get("guests_count")
        date = cleaned_data.get("date")
        time = cleaned_data.get("time")

        if not all([table, booking_type, guests_count, date, time]):
            return cleaned_data

        limits = {
            "DINNER": 5,
            "BANQUET": 15,
            "JUBILEE": 15,
        }

        max_allowed = limits.get(booking_type, 5)
        if guests_count > max_allowed:
            cleaned_data["guests_count"] = max_allowed
            self.add_error("guests_count", f"Максимум гостей для {booking_type.lower()} — {max_allowed}")

        start_dt = timezone.make_aware(datetime.combine(date, time))
        duration = {
            "DINNER": timedelta(hours=1, minutes=30),
            "BANQUET": timedelta(hours=5),
            "JUBILEE": timedelta(hours=5),
        }.get(booking_type, timedelta(hours=1, minutes=30))
        end_dt = start_dt + duration

        existing_bookings = TableBooking.objects.filter(table=table, date=date)

        for booking in existing_bookings:
            if not (end_dt <= booking.start_datetime or start_dt >= booking.end_datetime):
                raise forms.ValidationError("Этот столик уже занят в выбранный период времени.")

        return cleaned_data


