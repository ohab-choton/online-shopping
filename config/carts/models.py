from django.db import models
from store.models import Product,Variation
from account.models import UserAccount

# Create your models here.
class Cart(models.Model):
    user=models.ForeignKey(UserAccount, on_delete=models.CASCADE, null=True, blank=True)
    cart_id = models.CharField(max_length=255,blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id
    
    def total_quantity(self):
        total_dict = self.cartitem_set.aggregate(total=models.Sum('quantity'))
        return total_dict['total'] if total_dict['total'] is not None else 0
    
    # Unique product count (যতটা পণ্য add করা হয়েছে)
    def total_items(self):
        return self.cartitem_set.count()

    
class CartItem(models.Model):
    product=models.ForeignKey(Product, on_delete=models.CASCADE,db_index=True)
    variation=models.ManyToManyField(Variation,blank=True,db_index=True)
    cart=models.ForeignKey(Cart,on_delete=models.CASCADE,db_index=True)
    quantity=models.PositiveIntegerField()
    is_active=models.BooleanField(default=True)

    

    def sub_total(self):
        return self.product.price * self.quantity
    
    def __str__(self):
        return self.product.name
    
    