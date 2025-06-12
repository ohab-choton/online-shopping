from django.db import models
from account.models import UserAccount
from store.models import Product,Variation,ProductVariant
from carts.models import *

# Create your models here.
class Payment(models.Model):
   PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]
   PAYMENT_METHOD_CHOICES = [
        ('bkash', 'Bkash'),
        ('paypal', 'PayPal'),
        ('cash_on', 'Cash On'),
    ] 
   user= models.ForeignKey(UserAccount, on_delete=models.CASCADE) 
   payment_id = models.CharField(max_length=100, unique=True,null=True, blank=True)
   amount = models.DecimalField(max_digits=10, decimal_places=2)
   status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES)
   payment_method  = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
   created_at = models.DateTimeField(auto_now_add=True)

   def __str__(self):
        
        """String representation of the Payment model."""
        return f"Payment {self.payment_method} {self.payment_id} - {self.status} "
   


class Order(models.Model):

    ORDER_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE,db_index=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True,db_index=True)
    order_number =models.CharField(max_length=100, unique=True, null=True, blank=True)
    status=models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES,default='pending')
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    order_total= models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    #billing address
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=50)
    phone = models.CharField(max_length=15)
    address_line_1 = models.CharField(max_length=255, blank=True, null=True)
    country= models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    order_note = models.TextField(blank=True, null=True)
    shipping_cost=models.DecimalField(max_digits=10, decimal_places=2, default=0.00)



    def __str__(self):
        return self.user.first_name


class OrderProduct(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE,db_index=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE,db_index=True)
    user=models.ForeignKey(UserAccount,on_delete=models.CASCADE,db_index=True)
    variation=models.ManyToManyField(Variation,blank=True,db_index=True)
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, null=True, blank=True,db_index=True)
    color=models.CharField(max_length=50)
    size=models.CharField(max_length=50)
    quantity= models.PositiveIntegerField()

    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.product.name
    

   
