from django.contrib import admin
from .models import Product
from .models import Profile
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'holiday_discount_price', 'is_holiday_discount_active')
    list_editable = ('holiday_discount_price', 'is_holiday_discount_active')


admin.site.register(Product)
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'balance', 'payment_password')
    search_fields = ('user__username',)