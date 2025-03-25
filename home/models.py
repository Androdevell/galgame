from django.db import models
from datetime import date
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image_url = models.URLField(max_length=200, blank=True)
    holiday_discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_holiday_discount_active = models.BooleanField(default=False)
    discount_percent = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    def get_price(self):
        """返回折扣后的价格（如果适用）"""
        if self.is_holiday_discount_active and self.holiday_discount_price:
            return self.holiday_discount_price
        return self.price

    def __str__(self):
        return self.name
