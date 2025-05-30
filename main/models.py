from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta
from django.db import models
import os


class Category(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Название категории")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to="categories/", blank=True, null=True, verbose_name="Изображение")

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название продукта")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="products", verbose_name="Категория")
    description = models.TextField(blank=True, verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to="products/", blank=True, null=True, verbose_name="Изображение")

    def __str__(self):
        return self.name


class Review(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Пользователь")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="reviews", verbose_name="Продукт")
    score = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], verbose_name="Оценка")
    text = models.TextField(blank=True, null=True, verbose_name="Комментарий")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        unique_together = ("user", "product")  # Один пользователь может оставить только один отзыв на продукт

    def __str__(self):
        return f"Отзыв {self.score} от {self.user.username} для {self.product.name}"


class Table(models.Model):
    number = models.PositiveIntegerField(unique=True, verbose_name="Номер столика")
    location = models.CharField(max_length=100, verbose_name="Расположение", blank=True)
    seats = models.PositiveIntegerField(default=2, verbose_name="Количество мест")

    def __str__(self):
        return f"Столик #{self.number} ({self.seats} мест, {self.location})"


class TableBooking(models.Model):
    BOOKING_TYPES = [
        ("DINNER", "Обычный ужин"),
        ("BANQUET", "Банкет"),
        ("JUBILEE", "Юбилей"),
    ]

    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name="Пользователь")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    table = models.ForeignKey(Table, on_delete=models.CASCADE, related_name='bookings', verbose_name="Столик")
    booking_type = models.CharField(max_length=20, choices=BOOKING_TYPES, verbose_name="Тип брони")
    guests_count = models.PositiveIntegerField(verbose_name="Количество гостей")
    date = models.DateField(verbose_name="Дата")
    time = models.TimeField(verbose_name="Время начала")

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def start_datetime(self):
        return timezone.make_aware(datetime.combine(self.date, self.time))

    @property
    def end_datetime(self):
        duration = {
            "DINNER": timedelta(hours=1, minutes=30),
            "BANQUET": timedelta(hours=5),
            "JUBILEE": timedelta(hours=5),
        }.get(self.booking_type, timedelta(hours=1, minutes=30))
        return self.start_datetime + duration

    def __str__(self):
        return f"{self.get_booking_type_display()} на {self.date} в {self.time} ({self.guests_count} гостей)"


def special_offer_image_path(instance, filename):
    """
    Формирует путь для загрузки изображения с датой начала акции.
    Пример пути: specials/2024-03-15/image.jpg
    """
    date_folder = instance.date_starting.strftime("%Y-%m-%d")  # Форматируем дату
    return os.path.join("specials", date_folder, filename)


class SpecialOffers(models.Model):
    date_starting = models.DateTimeField(verbose_name="Дата начала акции")
    date_ending = models.DateTimeField(verbose_name="Дата окончания акции")
    image = models.ImageField(upload_to="specials/", blank=False, null=False, verbose_name="Изображение")

class EmailCampaign(models.Model):
    subject = models.CharField(max_length=255)
    message = models.TextField()
    image = models.ImageField(upload_to='email_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    sent = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.subject} ({'отправлено' if self.sent else 'не отправлено'})"