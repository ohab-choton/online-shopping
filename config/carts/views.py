from django.shortcuts import render, get_object_or_404, redirect
from store.models import Product,Variation,ProductVariant
from .models import Cart, CartItem
from django.http import HttpResponseNotFound,HttpResponse
from django.urls import reverse
from django.contrib import messages



# Create your views here.

def _cart_id(request):
    if not request.session.session_key:    # ১. সরাসরি সেশন কী চেক
        request.session.create()          # ২. প্রয়োজনে তৈরি
    return request.session.session_key    # ৩. কী রিটার্ন

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    product_variations = []
    # Current URL পেতে (যে পেজ থেকে রিকোয়েস্ট আসছে)
    redirect_url = request.META.get('HTTP_REFERER', reverse('cart'))
    selected_stock = None 

     # Init করা দরকার, না হলে UnboundLocalError হতে পারে
    color_variation = None
    size_variation = None

    if request.method =='POST':
        color=request.POST.get('color')
        size=request.POST.get('size')

        if color:
            color_variation=Variation.objects.get(product=product,variation_category__iexact='color',variation_value__iexact=color,is_active=True)
            product_variations.append(color_variation)

        if size:
            size_variation=Variation.objects.get(product=product,variation_category__iexact='size',variation_value__iexact=size,is_active=True)
            product_variations.append(size_variation)

        variant = None


        if color_variation  and size_variation:
            # ✅ ProductVariant মডেল থেকে সঠিক ভ্যারিয়েন্ট খুঁজুন
            variant = ProductVariant.objects.filter(
                product=product,
                color=color_variation,
                size=size_variation
            ).first()
            #stock a variant check ase kinh
            if variant:
                if variant.stock < 1:
                    messages.error(request, "এই রঙ এবং সাইজের জন্য পণ্য স্টকে নেই!")
                    return redirect(redirect_url)
                selected_stock = variant.stock
            else:
                 messages.error(request, "এই রঙ এবং সাইজের জন্য পণ্য খুঁজে পাওয়া যায়নি!")
                 return redirect(redirect_url)
        
                   

    # ✅ URL ভ্যালিডেশন: শুধু নিজের ডোমেইনের URL-এ রিডাইরেক্ট করুন
    from django.utils.http import url_has_allowed_host_and_scheme
    if not url_has_allowed_host_and_scheme(
        url=redirect_url,
        allowed_hosts={request.get_host()},  # শুধু বর্তমান হোস্ট (যেমন: localhost:8000)
        require_https=request.is_secure(),
    ):
        redirect_url = reverse('cart')  # অকার্যকর URL হলে কার্টে রিডাইরেক্ট


    try:
        if request.user.is_authenticated:
            # লগিন ইউজারের জন্য কার্ট
            cart = Cart.objects.get(user=request.user)
        else:
            # অ্যানোনিমাস ইউজারের জন্য সেশন-বেজড কার্ট
            cart = Cart.objects.get(cart_id=_cart_id(request))
        
    except Cart.DoesNotExist:
        cart = Cart.objects.create(
            user=request.user if request.user.is_authenticated else None,
            cart_id=_cart_id(request)
            )
    # ✅ পুরানো CartItem আছে কিনা variation সহ চেক করা
    existing_cart_items = CartItem.objects.filter(product=product, cart=cart)
    cart_item = None
    for item in existing_cart_items:
        if list(item.variation.all()) == product_variations:
            cart_item = item
            break

    # ✅ CartItem তৈরি বা update
    if cart_item:
        cart_item.quantity += 1
        cart_item.save()
    else:
        cart_item = CartItem.objects.create(
            product=product,
            quantity=1,
            cart=cart,
        )
        cart_item.variation.set(product_variations)
        cart_item.save()

    # ✅ Session update ও message
    request.session.modified = True
    messages.success(request, f"{product.name} কার্টে যোগ হয়েছে!")
    # ✅ যদি রিকোয়েস্টটা product details পেজ থেকে আসে, তাহলে context সহ পেজ দেখাও
    if 'product' in redirect_url:
        sizes = Variation.objects.filter(product=product, variation_category='size')
        colors = Variation.objects.filter(product=product, variation_category='color')
        return render(request, 'store/product-detail.html', {
            'product': product,
            'sizes': sizes,
            'colors': colors,
            'selected_stock': selected_stock,
        })

    return redirect(redirect_url)



def cart_view(request):
    total = 0
    quantity = 0
    cart_items = None
    shipping = 0
    grand_total = 0
   


    shipping_location = request.session.get('shipping_location', 'inside_dhaka')
    if request.method == 'POST':
        # শিপিং লোকেশন আপডেট করুন
        shipping_location = request.POST.get('shipping_location', 'inside_dhaka')
        request.session['shipping_location'] = shipping_location

    
    try:
        if request.user.is_authenticated:
            # লগিন ইউজারের কার্ট এবং আইটেম ফেচ করুন
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        else:
            # অ্যানোনিমাস ইউজারের জন্য সেশন-বেজড কার্ট
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        
        # টোটাল এবং কোয়ান্টিটি ক্যালকুলেট (উভয় কেসের জন্য)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

        if shipping_location == 'inside_dhaka':
            shipping = 60
        elif shipping_location == 'outside_dhaka':
            shipping = 120
        
        grand_total = total + shipping
        
    
    except Cart.DoesNotExist:
        pass  # কার্ট না থাকলে কিছু করবেন না
    
    context = {
        
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'shipping': shipping,
        'grand_total': grand_total,
        'shipping_location': shipping_location,
    }
    return render(request, 'carts/cart.html', context)



def update_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.method == "POST":
        action = request.POST.get('action')
        if action == "increase":
            cart_item.quantity += 1
        elif action == "decrease":
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
        cart_item.save()
    
    return redirect('cart')  

def remove_cart_item(request, item_id):
        try:
            if request.user.is_authenticated:
                cart=Cart.objects.get(user=request.user)
            else:
                cart=Cart.objects.get(cart_id=_cart_id(request))

            cart_item=get_object_or_404(CartItem, id=item_id, cart=cart)
            cart_item.delete()
        except Cart.DoesNotExist:
            return HttpResponseNotFound("Cart item does not exist")
        return redirect('cart')


