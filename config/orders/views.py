from django.shortcuts import render, redirect
from carts.models import Cart, CartItem
from .forms import OrderForm, PaymentForm
from .models import Order, OrderProduct, Payment
from store.models import Product,ProductVariant

from datetime import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import json
from django.http import JsonResponse
from carts.cart_utils import get_cart_context 
from django.urls import reverse

# Create your views here.



@login_required
def place_order(request):
    current_user = request.user
    print("Current User:", current_user)
    order = None  


    # Get cart context from utility
    cart_context = get_cart_context(request)
    cart_items = cart_context['cart_items']
    cart_count = cart_context['cart_count'] 

    print("Cart Items:", cart_items)
    print("Cart Count:", cart_count)

    cart_count = len(cart_items)
    if cart_count <= 0:
        return redirect('store')

    shipping_location = cart_context['shipping_location']

    if request.method == 'POST':
        # Update shipping location if changed
        new_location = request.POST.get('shipping_location', shipping_location)
        if new_location != shipping_location:
            request.session['shipping_location'] = new_location
            # Recalculate cart with new shipping location
            cart_context = get_cart_context(request)
        # Extract values from cart context
        total = cart_context['total']
        quantity = cart_context['quantity']
        shipping = cart_context['shipping']
        grand_total = cart_context['grand_total']



        
        form = OrderForm(request.POST)
        payment_form=PaymentForm(request.POST)
        if form.is_valid() and payment_form.is_valid():
            payment_method = payment_form.cleaned_data['payment_method']
            payment = Payment.objects.create(
            user=current_user,
            payment_method=payment_method,
            amount=grand_total,
            status='pending',
    )

            order = Order.objects.create(
                user=current_user,
                payment=payment,  # ✅ Attach the created payment
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address_line_1=form.cleaned_data['address_line_1'],
                country=form.cleaned_data['country'],
                state=form.cleaned_data['state'],
                city=form.cleaned_data['city'],
                order_note=form.cleaned_data['order_note'],
                order_total=grand_total,
                shipping_cost=shipping,
                is_ordered=False,
            )

            # Generate order number
            current_date = datetime.today().strftime("%Y-%m-%d")
            order_number = current_date + str(order.id)
            order.order_number = order_number
            order.save()

            # Save to session and redirect
            request.session['order_id'] = order.id
            request.session.modified = True 
            return proceed_to_payment(request)

    else:
        form = OrderForm()
        order_id = request.session.get('order_id')
        if order_id:
            try:
                order = Order.objects.get(id=order_id, user=current_user, is_ordered=False)
            except Order.DoesNotExist:
                order = None

    # Calculate cart summary
    totals = get_cart_context(request)
    total = totals['total']
    quantity = totals['quantity']
    shipping = totals['shipping']
    grand_total = totals['grand_total']

    context = {
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
        'cart_items': cart_items,
        'cart_count': cart_count,
        'form': form,
        'payment_form': PaymentForm(),
        'total': total,
        'quantity': quantity,
        'shipping': shipping,
        'grand_total': grand_total,
        'shipping_location': shipping_location,
        'order': order,
        'order_number': order.order_number if order else None
        
        
    }
    return render(request, 'orders/payments.html', context)


        
        
def proceed_to_payment(request):
    print("Entered proceed_to_payment")
    order_id = request.session.get('order_id')
    if not order_id:
        return redirect('checkout')
    order = Order.objects.get(id=order_id)
    print("Request Method:", request.method)
    if request.method == 'POST':
        print(f"Request method: {request.method}")
        print(f"Request headers: {request.headers}")
        print(f"POST data: {request.POST}")
        # 1. If PayPal sends data via JavaScript
        if request.headers.get('Content-Type') == 'application/json':
            data = json.loads(request.body)
            try:
                # Find the order
                order = Order.objects.get(user=request.user, is_ordered=False, order_number=data['orderID'])
                # Create payment
                payment = Payment.objects.create(
                    user=request.user,
                    payment_id=data['transactionId'],
                    payment_method=data['paymentMethod'],
                    amount=order.order_total,
                    status=data['status']
                )

                # Update order
                order.payment = payment
                order.is_ordered = True
                order.status = 'processing'
                order.save()

                # Move cart items to OrderProduct
                cart_items = CartItem.objects.filter(cart__user=request.user)
                for item in cart_items:
                    order_product = OrderProduct.objects.create(
                        order=order,
                        payment=payment,
                        user=request.user,
                        product=item.product,
                        quantity=item.quantity,
                        product_price=item.product.price,
                        ordered=True
                    )
                    order_product.variation.set(item.variation.all())

                    #reduce product 
                    product=Product.objects.get(id=item.product.id)
                    if product.stock >= item.quantity:
                                product.stock -= item.quantity
                                product.save()
                    else:
                        messages.error(request, "Insufficient stock for product: {}".format(item.product.name))

                    if item.variation.exists():
                                color=item.variation.filter(variation_category__iexact='color').first()
                                size=item.variation.filter(variation_category__iexact='size').first()
                                try:
                                    variant=ProductVariant.objects.get(
                                        product=product,
                                        color=color if color else None,
                                        size=size if size else None
                                    )
                                    if variant.stock >= item.quantity:
                                        variant.stock -= item.quantity
                                        variant.save()
                                except ProductVariant.DoesNotExist:
                                    print("Product variant not found for item:", item.product.name)
                                    messages.error(request, "Product variant not found.")
                # Clear cart
                cart_items.delete()


                # send order number and transaction Id back to send data method via jason response
                data={
                     'order_number': order.order_number,
                     'transaction_id': payment.payment_id,
                     
                }

                return JsonResponse({'status': 'success', 'data': data})

            except Exception as e:
                return JsonResponse({'status': 'failed', 'message': str(e)})
        else:
            form = OrderForm(request.POST)
            payment_form = PaymentForm(request.POST)
            print("Form data:", request.POST)
            print("Payment Form data:", payment_form.data)
            if form.is_valid() and payment_form.is_valid():
                print("Both forms are valid")
                try:
                    order_id = request.session.get('order_id')
                    order = Order.objects.get(id=order_id, user=request.user, is_ordered=False)
                    cart = Cart.objects.get(user=request.user)
                    cart_items = CartItem.objects.filter(cart=cart, is_active=True)
                except Cart.DoesNotExist:
                    messages.error(request, "Cart not found.")
                    return redirect('store')
                if not cart_items.exists():
                    messages.error(request, "Your cart is empty.")
                    return redirect('store')
                # Calculate order total BEFORE creating order
                cart_context = get_cart_context(request)
                order_total = cart_context['grand_total']
               
                order.order_number = datetime.today().strftime("%Y%m%d") + str(order.id)
                order.save()
              
                payment_method = payment_form.cleaned_data['payment_method']
                print("Payment Method:", payment_method)
                if payment_method == 'cash_on':
                    payment = Payment.objects.create(
                        user=request.user,
                        payment_method='cash_on',
                        amount=order_total,
                        status='completed',
                        payment_id='COD-' + order.order_number,
                    )
                    order.payment = payment
                    order.status = 'processing'
                    order.is_ordered = True
                    order.save()
                    for item in cart_items:
                         order_product = OrderProduct.objects.create(
                            order=order,
                            payment=payment,
                            user=request.user,
                            product=item.product,
                            quantity=item.quantity,
                            product_price=item.product.price,
                            ordered=True,
                            
                        )
                         order_product.variation.set(item.variation.all())

                         #reduce product 
                         product=Product.objects.get(id=item.product.id)
                         if product.stock >= item.quantity:
                                product.stock -= item.quantity
                                product.save()
                         else:
                            messages.error(request, "Insufficient stock for product: {}".format(item.product.name))
                         if item.variation.exists():
                                color=item.variation.filter(variation_category__iexact='color').first()
                                size=item.variation.filter(variation_category__iexact='size').first()
                                try:
                                    variant=ProductVariant.objects.get(
                                        product=product,
                                        color=color if color else None,
                                        size=size if size else None
                                    )
                                    if variant.stock >= item.quantity:
                                        variant.stock -= item.quantity
                                        variant.save()
                                except ProductVariant.DoesNotExist:
                                    print("Product variant not found for item:", item.product.name)
                                    messages.error(request, "Product variant not found.")
    
                    # Clear cart items and delete cart    
                    cart_items.delete()
                    Cart.objects.filter(user=request.user).delete()
                    messages.success(request, "Your order has been placed with Cash on Delivery.")


                    context = {
                        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
                        'cart_items': [],
                        'cart_count': 0,
                        'form': form,
                        'payment_form': payment_form,
                        'total': order.order_total,
                        'quantity': 0,
                        'shipping_cost': order.shipping_cost,
                        'grand_total': order.order_total,
                        'shipping_location': order.address_line_1,
                        'order': order,
                        'order_number': order.order_number,
                    }
                    return redirect(f"{reverse('order-complete')}?order_number={order.order_number}&payment_method={payment.payment_id}")
                        
                elif payment_method == 'paypal':
                    payment = Payment.objects.create(
                        user=request.user,
                        payment_method='paypal',
                        amount=order_total,
                        status='pending',
                        
                    )
                    order.payment = payment
                    order.status = 'pending'
                    order.is_ordered = False
                    order.save()
                    context = {
                                'paypal_client_id': settings.PAYPAL_CLIENT_ID,
                                'cart_items': list(cart_items) if 'cart_items' in locals() else [],
                                'cart_count': cart_items.count() if 'cart_items' in locals() else 0,
                                'form': form,
                                'payment_form': payment_form,
                                'total': order.order_total,
                                'quantity': sum([item.quantity for item in cart_items]) if 'cart_items' in locals() else 0,
                                'shipping': order.shipping_cost,
                                'grand_total': order.order_total,
                                'shipping_location': order.address_line_1,
                                'order': order,
                                'order_number': order.order_number,
                                }
                    return render(request, 'orders/payments.html', context)
                else:  
                    messages.error(request, "Invalid payment method selected.")
                    return redirect('index')
            else:
                print("Form errors:", form.errors)
                print("Payment Form errors:", payment_form.errors)
                messages.error(request, "Form validation failed.")
                return redirect('index')

    return redirect('index')


def order_complete(request):
      order_number = request.GET.get('order_number')
      transaction_id = request.GET.get('payment_method')

      try:
           order= Order.objects.get(order_number=order_number, is_ordered=True)
           order_products = OrderProduct.objects.filter(order_id=order.id)
           payment= Payment.objects.get(payment_id=transaction_id)

           cartsummary= get_cart_context(request)
           total= cartsummary['total']
           grand_total = cartsummary['grand_total']
           shipping_location = cartsummary['shipping_location']
           shipping_cost = cartsummary['shipping']


           context={
                'order': order,
                'order_products': order_products,
                'order_number': order.order_number,
                'transaction_id': payment.payment_id,
                'payment': payment,
                'grand_total': order.order_total,
               
                'shipping_location': order.address_line_1,
                'shipping_cost': order.shipping_cost, 

           }

      except (Order.DoesNotExist,Payment.DoesNotExist):
            messages.error(request, "Order not found or payment not completed.")
            return redirect('store',context)




    
      return render(request, 'orders/order_complete.html', context)
       
       
    

    


    
