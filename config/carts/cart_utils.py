# carts/cart_utils.py
from .models import Cart, CartItem

def get_cart_context(request):
    total = 0
    quantity = 0
    cart_items = []
    shipping = 0
    grand_total = 0
    shipping_location = request.session.get('shipping_location', 'inside_dhaka')

    try:
        if request.user.is_authenticated:
            # For logged-in users
            cart = Cart.objects.get(user=request.user)
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        else:
            # For anonymous users
            cart_id = request.session.get('cart_id')
            if cart_id:
                cart = Cart.objects.get(cart_id=cart_id)
                cart_items = CartItem.objects.filter(cart=cart, is_active=True)

        for cart_item in cart_items:
            total += cart_item.product.price * cart_item.quantity
            quantity += cart_item.quantity

        if shipping_location == 'inside_dhaka':
            shipping = 60
        elif shipping_location == 'outside_dhaka':
            shipping = 120

        grand_total = total + shipping

    except Cart.DoesNotExist:
        # Cart doesn't exist, use default values
        pass

    return {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'cart_count': len(cart_items),
        'shipping': shipping,
        'grand_total': grand_total,
        'shipping_location': shipping_location,
    }