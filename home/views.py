from django.shortcuts import render,HttpResponse,get_object_or_404,redirect
from .models import Product
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib import messages
from .models import Product, Cart, CartItem
from .models import Order, OrderItem, Profile
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache

from decimal import Decimal
import uuid
# Create your views here.
def index(request):
    return render(request,"index.html")

def index(request):
    products = Product.objects.all()  # 获取所有产品
    return render(request, 'index.html', {'products': products})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})


@csrf_exempt  # 仅用于测试，生产环境建议使用正确的 CSRF 处理
def user_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return JsonResponse({"success": True})
        else:
            return JsonResponse({"success": False, "error": "用户名或密码错误"})
    return JsonResponse({"success": False, "error": "仅支持POST请求"})
@csrf_exempt  # 开发测试时使用，生产环境建议正确配置CSRF保护
def user_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        if User.objects.filter(username=username).exists():
            return JsonResponse({"success": False, "error": "用户名已存在"})
        try:
            User.objects.create_user(username=username, password=password)
            return JsonResponse({"success": True})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})
    return JsonResponse({"success": False, "error": "仅支持POST请求"})


def search_products(request):
    query = request.GET.get('q', '')
    products = []

    if query:
        # 使用Q对象进行复杂查询（名称或描述中包含查询文本）
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'products': products,
    }
    return render(request, 'search_results.html', context)


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'cart.html', {'cart': cart})

@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart.objects.get(user=request.user)

    # 检查商品是否已经在购物车中
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )

    # 如果商品已存在，则增加数量
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total_price()
        })
    return redirect('cart_view')


@login_required
def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart = cart_item.cart

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
        else:
            cart_item.delete()

        # 处理AJAX请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_total': cart.get_total_price(),
                'item_subtotal': cart_item.get_cost()
            })

    return redirect('cart_view')

@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'cart_total': cart.get_total_price()
        })
    return redirect('cart_view')


@login_required
def update_profile(request):
    # 确保当前用户有 Profile 对象，如果没有则创建一个
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user = request.user
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')

        # 更新用户信息
        if email:
            user.email = email
        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        user.save()

        # 如果你需要更新 Profile 中其他字段，可以在这里添加处理逻辑，例如：
        # phone = request.POST.get('phone')
        # if phone:
        #     profile.phone = phone
        # profile.save()
        new_payment_password = request.POST.get('new_payment_password')
        if new_payment_password:
            if len(new_payment_password) != 6 or not new_payment_password.isdigit():
                messages.error(request, "支付密码必须为6位数字")
            else:
                profile.payment_password = new_payment_password
                profile.save()
                messages.success(request, "支付密码更新成功！")
        else:
            messages.success(request, "个人信息更新成功！")
        return redirect('profile')

    return render(request, 'profile.html')

def orders_view(request):
    # 假设有一个 Order 模型，并且用户订单可以通过 user.orders.all() 获取
    orders = request.user.orders.all()
    return render(request, 'orders.html', {'orders': orders})


# checkout 视图示例 (部分代码)
@login_required
def checkout(request):
    # 获取当前用户的购物车
    cart, created = Cart.objects.get_or_create(user=request.user)
    total_price = cart.get_total_price()
    cart_total = cart.get_total_price()
    print(total_price)
    print(cart_total)
    if request.method == 'POST':
        payment_method = request.POST.get('payment_method')

        # 余额支付处理
        if payment_method == 'balance':
            input_password = request.POST.get('payment_password')
            profile, created = Profile.objects.get_or_create(user=request.user)
            if not profile.payment_password:
                messages.error(request, "您还未设置支付密码，请先设置支付密码。")
                return redirect('checkout')
            if input_password != profile.payment_password:
                messages.error(request, "支付密码错误，请重新输入。")
                return redirect('checkout')
            if profile.balance < cart_total:
                messages.error(request, "余额不足，请选择其他支付方式或充值。")
                return redirect('checkout')
            # 扣除余额（确保类型匹配）
            profile.balance -= cart_total
            profile.save()

        # 其他支付方式逻辑可以在这里补充

        # 生成唯一订单号
        order_number = str(uuid.uuid4()).replace('-', '').upper()[:20]
        order = Order.objects.create(
            user=request.user,
            order_number=order_number,
            total_amount=cart_total,
            status='pending'
        )

        # 将购物车中的每个 CartItem 转为订单项
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=(cart_item.product.holiday_discount_price
                       if cart_item.product.is_holiday_discount_active and cart_item.product.holiday_discount_price
                       else cart_item.product.price)
            )
        # 清空购物车
        cart.items.all().delete()

        messages.success(request, f"订单 {order.order_number} 创建成功！")
        return redirect('orders')
        # 获取用户余额
    profile, created = Profile.objects.get_or_create(user=request.user)
    balance = profile.balance
    return render(request, 'checkout.html', {'total_price': total_price, 'balance': balance})

@login_required
def order_detail(request, order_id):
    # 确保订单只允许对应用户查看
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_detail.html', {'order': order})