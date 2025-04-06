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


# 订单模型，关联用户，每个订单有唯一订单号和总金额
class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('pending', '待付款'),
        ('processing', '处理中'),
        ('completed', '已完成'),
        ('cancelled', '已取消'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=20, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES, default='pending')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"订单 {self.order_number} - {self.user.username}"

# 订单项模型，一个订单可以有多个订单项，每个订单项关联一个产品
class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    # 此处记录下单时的单价，方便订单统计（即使产品价格后续发生变化）
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"

# 如果你需要扩展用户模型，添加额外的资料信息，可以使用 OneToOne 关联方式建立 Profile 模型
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # 可以在这里添加额外的字段，例如电话号码、地址等
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)  # 用户余额
    payment_password = models.CharField(max_length=6, blank=True)  # 注意：实际项目中建议加密存储
    def __str__(self):
        return f"{self.user.username} 的个人资料"

# 当 User 对象创建时，同时创建一个 Profile 对象
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# 保存 User 对象时，同时保存关联的 Profile 对象
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
