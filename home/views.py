from django.shortcuts import render,HttpResponse,get_object_or_404
from .models import Product
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
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