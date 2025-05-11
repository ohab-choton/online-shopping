# cart/context_processors.py
from .models import Cart, CartItem

# created for cart counter
def cart_counter(request):
    cart_count = 0
    if request.user.is_authenticated:
        # লগিন ইউজারের জন্য কার্ট কাউন্ট
        cart = Cart.objects.filter(user=request.user).first()
    else:
        # সেশন-বেজড কার্ট (অ্যানোনিমাস ইউজার)
        cart_id = request.session.session_key
        if not cart_id:
            request.session.create()
            cart_id = request.session.session_key
        cart = Cart.objects.filter(cart_id=cart_id).first()
    
    if cart:
        cart_count = cart.total_items()
    return {'cart_count': cart_count}