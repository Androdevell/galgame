from django.shortcuts import render,HttpResponse
from .models import Product
# Create your views here.
def index(request):
    return render(request,"index.html")

def index(request):
    products = Product.objects.all()  # 获取所有产品
    return render(request, 'index.html', {'products': products})