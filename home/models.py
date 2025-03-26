from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    stock = models.IntegerField(default=20)
    image_url = models.URLField(max_length=200, blank=True)
    desimage_url = models.URLField(max_length=200, blank=True)
    holiday_discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    is_holiday_discount_active = models.BooleanField(default=False)
    discount_percent = models.DecimalField(max_digits=10, decimal_places=0, blank=True, null=True)
    def get_price(self):
        """返回折扣后的价格（如果适用）"""
        if self.is_holiday_discount_active and self.holiday_discount_price:
            return self.holiday_discount_price
        return self.price
    def get_discount_percent(self):
        """返回折扣后的价格（如果适用）"""
        return 100-int((self.holiday_discount_price/self.price)*100)


    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}的购物车"

    def get_total_price(self):
        return sum(item.get_cost() for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    def get_cost(self):
        if self.product.is_holiday_discount_active and self.product.holiday_discount_price:
            return self.product.holiday_discount_price* self.quantity
        return self.product.price * self.quantity

# 用信号确保每个用户都有一个购物车
@receiver(post_save, sender=User)
def create_user_cart(sender, instance, created, **kwargs):
    if created:
        Cart.objects.create(user=instance)

