from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import models
from django.conf import settings


# class User(AbstractUser):
#     phone = models.CharField(max_length=15, unique=True, verbose_name="Номер телефона")

#     class Meta:
#         swappable = "AUTH_USER_MODEL"

#     def __str__(self):
#         return self.username


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



class TableBooking(models.Model):
    name = models.CharField(max_length=255, blank=True, verbose_name="Имя")
    phone = models.CharField(max_length=15, blank=True, verbose_name="Телефон")

    def __str__(self):
        return f"Бронь на имя {self.name}, номер телефона - {self.phone}"
