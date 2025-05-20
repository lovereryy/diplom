from django.contrib import admin
from .models import Category, Product, Review, TableBooking, SpecialOffers, Table
from django.urls import reverse
from django.utils.html import format_html

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price')
    search_fields = ('name', 'category__name')
    list_filter = ('category',)

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'text', 'score', 'created_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('score', 'created_at')

@admin.register(Table)
class TableAdmin(admin.ModelAdmin):
    list_display = ('number', 'seats', 'location')

@admin.register(TableBooking)
class TableBookingAdmin(admin.ModelAdmin):
    list_display = ('user', 'booking_type', 'date', 'time', 'guests_count', 'table', 'phone')
    list_filter = ('booking_type', 'date')
    search_fields = ('user__username', 'phone')

    readonly_fields = ('linked_user',)

    fieldsets = (
        (None, {
            'fields': ('linked_user', 'booking_type', 'guests_count', 'date', 'time', 'table', 'phone')
        }),
    )

    def linked_user(self, obj):
        if obj.user:
            url = reverse('admin:auth_user_change', args=[obj.user.id])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return "-"
    linked_user.short_description = 'Пользователь'

    
@admin.register(SpecialOffers)
class SpecialOffersAdmin(admin.ModelAdmin):
    list_display = ('date_starting', 'date_ending', 'image')
    list_filter = ('date_starting', 'date_ending')
    search_fields = ('date_starting', 'date_ending')