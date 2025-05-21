from django.contrib import admin
from .models import Category, Product, Review, TableBooking, SpecialOffers, Table,EmailCampaign
from django.urls import reverse
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from email.mime.image import MIMEImage
from django.utils.html import strip_tags
import os
from django.contrib.auth import get_user_model


User = get_user_model()

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


@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):
    list_display = ('subject', 'created_at', 'sent')
    actions = ['send_email_campaign']

    def send_email_campaign(self, request, queryset):
        for campaign in queryset:
            if not campaign.sent:
                users = User.objects.filter(is_active=True).exclude(email='')
                recipient_list = list(users.values_list('email', flat=True))

                # Создаём html с cid картинки
                if campaign.image:
                    cid = 'image1'  # Идентификатор картинки в письме
                    html_content = f"""
                        <p>{campaign.message}</p>
                        <img src="cid:{cid}" alt="Изображение" style="max-width:600px;">
                    """
                else:
                    html_content = f"<p>{campaign.message}</p>"

                plain_message = strip_tags(html_content)

                for email in recipient_list:
                    msg = EmailMultiAlternatives(
                        subject=campaign.subject,
                        body=plain_message,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[email],
                    )
                    msg.attach_alternative(html_content, "text/html")

                    if campaign.image:
                        with open(campaign.image.path, 'rb') as img_file:
                            img = MIMEImage(img_file.read())
                            img.add_header('Content-ID', f'<{cid}>')
                            img.add_header('Content-Disposition', 'inline', filename=os.path.basename(campaign.image.path))
                            msg.attach(img)

                    msg.send()

                campaign.sent = True
                campaign.save()
        self.message_user(request, "Рассылка отправлена успешно.")
    send_email_campaign.short_description = "Отправить выбранные рассылки"