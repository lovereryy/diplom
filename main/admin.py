from django.contrib import admin
from .models import Category, Product, Review, TableBooking, SpecialOffers

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

@admin.register(TableBooking)
class TableBookingAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone')
    search_fields = ('name', 'phone')

@admin.register(SpecialOffers)
class SpecialOffersAdmin(admin.ModelAdmin):
    list_display = ('date_starting', 'date_ending', 'image')
    list_filter = ('date_starting', 'date_ending')
    search_fields = ('date_starting', 'date_ending')