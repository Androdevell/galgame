from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'holiday_discount_price', 'is_holiday_discount_active')
    list_editable = ('holiday_discount_price', 'is_holiday_discount_active')


admin.site.register(Product)
