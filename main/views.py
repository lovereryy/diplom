from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import IntegrityError, OperationalError
from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
import logging
from django.contrib.auth import get_backends
from django.conf import settings

from telegram import Bot
import asyncio

from .models import Product, Category, Review, SpecialOffers
from .forms import ReviewForm, CustomUserChangeForm, CustomAuthenticationForm, CustomUserCreationForm, TableBookingForm

logger = logging.getLogger(__name__)
bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)

def home(request):

    if request.method == "POST":
        form = TableBookingForm(request.POST)
        if form.is_valid():
            table_booking = form.save()
            
            # Отправка сообщения в Telegram
            chat_id = settings.TELEGRAM_CHAT_ID
        

            message_text = (
                f"Новая заявка!\n\n"
                f"Имя: {table_booking.name}\n"
                f"Телефон: {table_booking.phone}\n"
            )
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(bot.send_message(chat_id, message_text))
                     
            return redirect('thanks')
    else:
        form = TableBookingForm()


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
            "form": form,
        })
    except OperationalError as e:
        logger.error(f"Ошибка базы данных: {e}")
        messages.error(request, "Ошибка загрузки данных. Попробуйте позже.")
        return redirect("home")


def product_detail(request, product_id):
    try:
        product = get_object_or_404(Product, id=product_id)
        reviews = product.reviews.all().order_by("-created_at")
        user_review = None  # Отзыв текущего пользователя
        form = None

        if request.user.is_authenticated:
            # Проверяем, есть ли у текущего пользователя уже отзыв к данному продукту
            user_review = product.reviews.filter(user=request.user).first()

            # Обработка POST-запроса
            if request.method == "POST":
                # Если это удаление отзыва
                if "delete_review" in request.POST and user_review:
                    user_review.delete()
                    messages.success(request, "Ваш отзыв удалён.")
                    return redirect("product_detail", product_id=product.id)
                else:
                    # Создаём или редактируем отзыв (instance=user_review)
                    form = ReviewForm(request.POST, instance=user_review)
                    if form.is_valid():
                        review = form.save(commit=False)
                        review.user = request.user
                        review.product = product
                        review.save()
                        messages.success(request, "Ваш отзыв сохранён!")
                        return redirect("product_detail", product_id=product.id)
                    else:
                        messages.error(request, "Ошибка валидации формы.")
            else:
                # GET-запрос: просто показываем форму, привязанную к user_review
                form = ReviewForm(instance=user_review)
        else:
            # Если пользователь не авторизован, форма не нужна
            form = None

        return render(request, "main/product_detail.html", {
            "product": product,
            "reviews": reviews,
            "form": form,
            "user_review": user_review,
        })

    except ObjectDoesNotExist:
        messages.error(request, "Продукт не найден.")
        return redirect("home")
    except Exception as e:
        messages.error(request, "Произошла ошибка. Попробуйте позже.")
        return redirect("home")


def register(request):
    try:
        if request.method == "POST":
            form = CustomUserCreationForm(request.POST)
            if form.is_valid():
                user = form.save()
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
    

def about(request):
    return render(request, "main/about.html")

def contacts(request):
    return render(request, "main/contacts.html")

def thanks(request):
    return render(request, "main/thanks.html")

def menu(request):
    try:
        categories = Category.objects.prefetch_related('products').all()

        return render(request, "main/menu.html", {
            "categories": categories,
        })
    except OperationalError as e:
        logger.error(f"Ошибка базы данных: {e}")
        messages.error(request, "Ошибка загрузки данных. Попробуйте позже.")
        return redirect("home")
    

def custom_404(request, exception):
    return render(request, "404.html", status=404)