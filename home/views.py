from django.shortcuts import render,HttpResponse,get_object_or_404,redirect
from .models import Product
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.contrib import messages
from .models import Product, Cart, CartItem,Profile
from django.contrib.auth.decorators import login_required
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

        messages.success(request, "个人信息已成功更新！")
        return redirect('profile')

    return render(request, 'profile.html')

def orders_view(request):
    # 假设有一个 Order 模型，并且用户订单可以通过 user.orders.all() 获取
    orders = request.user.orders.all()
    return render(request, 'orders.html', {'orders': orders})