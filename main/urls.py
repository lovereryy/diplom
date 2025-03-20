from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from .views import custom_404

urlpatterns = [
    path("", views.home, name="home"),  # Главная страница
    path("product/<int:product_id>/", views.product_detail, name="product_detail"),
    path("register/", views.register, name="register"),  # Регистрация
    path("login/", views.user_login, name="login"),  # Вход
    path("logout/", views.user_logout, name="logout"),  # Выход
    path("profile/", views.profile, name="profile"),  # Личный кабинет
    path("delete_account/", views.delete_account, name="delete_account"),
    path('contacts/', views.contacts, name='contacts'),
    path('about/', views.about, name='about'),
    path('menu/', views.menu, name='menu'),
    path('thanks/', views.thanks, name='thanks'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = custom_404