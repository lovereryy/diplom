from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path("", views.home, name="home"),  # Главная страница
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),  # Страница продукта
    path("register/", views.register, name="register"),  # Регистрация
    path("login/", views.user_login, name="login"),  # Вход
    path("logout/", views.user_logout, name="logout"),  # Выход
    path("profile/", views.profile, name="profile"),  # Личный кабинет
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)