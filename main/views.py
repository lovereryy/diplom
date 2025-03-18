from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError, OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import logging

from .models import Product, Category, Review, SpecialOffers
from .forms import ReviewForm, CustomUserChangeForm, CustomAuthenticationForm, CustomUserCreationForm

logger = logging.getLogger(__name__)

def home(request):
    try:
        categories = Category.objects.all()
        products = Product.objects.all()

        # Фильтруем спецпредложения, которые начались и ещё не закончились
        current_time = timezone.now()
        specials = SpecialOffers.objects.filter(date_starting__lte=current_time, date_ending__gte=current_time)

        return render(request, "main/home.html", {
            "categories": categories,
            "products": products,
            "specials": specials,
        })
    except OperationalError as e:
        logger.error(f"Ошибка базы данных: {e}")
        messages.error(request, "Ошибка загрузки данных. Попробуйте позже.")
        return redirect("home")


def product_detail(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        reviews = product.reviews.all()

        if request.user.is_authenticated:
            if request.method == "POST":
                form = ReviewForm(request.POST)
                if form.is_valid():
                    try:
                        review, created = Review.objects.get_or_create(
                            user=request.user, product=product,
                            defaults={"text": form.cleaned_data["text"], "score": form.cleaned_data["score"]}
                        )
                        if not created:
                            review.text = form.cleaned_data["text"]
                            review.score = form.cleaned_data["score"]
                            review.save()

                        messages.success(request, "Отзыв добавлен!")
                        return redirect("product_detail", product_id=product.id)
                    except IntegrityError:
                        messages.error(request, "Вы уже оставляли отзыв.")
                else:
                    messages.error(request, "Ошибка валидации формы.")
            else:
                form = ReviewForm()
        else:
            form = None

        return render(request, "main/product_detail.html", {"product": product, "reviews": reviews, "form": form})
    
    except ObjectDoesNotExist:
        messages.error(request, "Продукт не найден.")
        return redirect("home")
    except Exception as e:
        logger.exception(f"Ошибка в product_detail: {e}")
        messages.error(request, "Произошла ошибка. Попробуйте позже.")
        return redirect("home")


def register(request):
    try:
        if request.method == "POST":
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save(commit=False)
                user.username = user.email  # Используем email как username
                user.save()
                login(request, user)
                messages.success(request, "Вы успешно зарегистрировались!")
                return redirect("home")
            else:
                messages.error(request, "Ошибка регистрации. Проверьте введенные данные.")
        else:
            form = CustomUserCreationForm()
        return render(request, "main/register.html", {"form": form})

    except Exception as e:
        logger.exception(f"Ошибка при регистрации: {e}")
        messages.error(request, "Не удалось зарегистрироваться. Попробуйте позже.")
        return redirect("home")

def user_login(request):
    try:
        if request.method == "POST":
            form = CustomAuthenticationForm(request, data=request.POST)
            if form.is_valid():
                user = form.get_user()
                login(request, user)
                messages.success(request, "Вы вошли в систему!")
                return redirect("home")
            else:
                messages.error(request, "Ошибка авторизации. Проверьте данные.")
        else:
            form = CustomAuthenticationForm()
        return render(request, "main/login.html", {"form": form})

    except Exception as e:
        logger.exception(f"Ошибка при входе: {e}")
        messages.error(request, "Ошибка входа. Попробуйте позже.")
        return redirect("home")

@login_required
def user_logout(request):
    try:
        logout(request)
        messages.success(request, "Вы вышли из системы!")
    except Exception as e:
        logger.error(f"Ошибка при выходе: {e}")
        messages.error(request, "Ошибка выхода. Попробуйте позже.")
    return redirect("home")

@login_required
def profile(request):
    try:
        user = request.user  # Получаем текущего пользователя

        if request.method == "POST":
            form = CustomUserChangeForm(request.POST, instance=user)
            if form.is_valid():
                form.save()
                messages.success(request, "Ваши данные обновлены!")
                return redirect("profile")
            else:
                messages.error(request, "Ошибка валидации данных.")
        else:
            form = CustomUserChangeForm(instance=user)  # Загружаем данные пользователя

        return render(request, "main/profile.html", {"form": form})

    except Exception as e:
        logger.exception(f"Ошибка в profile: {e}")
        messages.error(request, "Не удалось обновить профиль. Попробуйте позже.")
        return redirect("profile")


@login_required
def delete_account(request):
    """Удаление аккаунта пользователя"""
    if request.method == "POST":
        user = request.user
        user.delete()
        messages.success(request, "Ваш аккаунт удален.")
        return redirect("home")  # Перенаправляем на главную

    return render(request, "main/delete_account.html")
    

def category_detail(request, category_id):
    try:
        category = get_object_or_404(Category, id=category_id)
        products = category.products.all()

        return render(request, "main/category_detail.html", {"category": category, "products": products})
    
    except ObjectDoesNotExist:
        messages.error(request, "Категория не найдена.")
        return redirect("home")
    except Exception as e:
        logger.exception(f"Ошибка в category_detail: {e}")
        messages.error(request, "Произошла ошибка. Попробуйте позже.")
        return redirect("home")


def about(request):
    return render(request, "main/about.html")

def contacts(request):
    return render(request, "main/contacts.html")