from django import forms
from .models import Review
from django.contrib.auth.models import User


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