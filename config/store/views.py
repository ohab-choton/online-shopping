from django.shortcuts import render, get_object_or_404
from .models import Category, Product, Banner
from carts.models import CartItem, Cart
from carts.views import _cart_id
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Create your views here.

def index(request):
    products=Product.objects.filter(is_available=True).order_by('-created_at')
    banners = Banner.objects.filter(show=True).order_by('-created_date') 

    context={
        'products': products,
        'banners': banners,
    }
    return render(request, 'store/home.html', context)


def product_details(request, slug):
    product = get_object_or_404(Product, slug=slug)

     # Initialize in_cart as False
    in_cart = False

    if request.user.is_authenticated:
        # Check if the product exists in the user's cart
        in_cart = CartItem.objects.filter(cart__user=request.user, product=product).exists()
    else:
     # For anonymous users, check using session cart_id
        cart_id = _cart_id(request)
        in_cart = CartItem.objects.filter(cart__cart_id=cart_id,  product=product).exists()

    context={
        'product': product,
        'in_cart': in_cart,
        
    }
    return render(request, 'store/product-detail.html',  context)

def store(request):
    products = Product.objects.filter(is_available=True).order_by('-created_at')
    products_count = products.count()  # Calculate once here (outside try-except)

    # Pagination
    paginator = Paginator(products, 2)
    page = request.GET.get('page')

    try:
        page_products = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page
        page_products = paginator.page(1)
    except EmptyPage:
        # If page is out of range, deliver last page
        page_products = paginator.page(paginator.num_pages)

    context = {
        #'page_products': page_products,
        'products': page_products,
        'paginator': paginator,
        'page': page,
        'products_count': products_count,  # Now always defined
    }
    return render(request, 'store/store.html', context)

def products_by_category(request, category_slug):
    category = get_object_or_404(Category, slug=category_slug)
    products = Product.objects.filter(category=category, is_available=True)

    context = {
        'category': category,
        'products': products,
        'products_count': products.count(),  # Count of products in this category
    }
    return render(request, 'store/store.html', context)






