from django.db import models
from django.utils.text import slugify
from django.utils.html import mark_safe
from django.urls import reverse

# Create your models here.

class Category(models.Model):
    name =models.CharField(max_length=100, unique=True,blank=False,null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='category_images/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def save(self,*args,**kwarges):
        if not self.slug:
            self.slug=slugify(self.name)
        super(Category,self).save(*args,**kwarges)

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="{}" width="50" height="50" />'.format(self.image.url))
        return ''
    
    def get_url(self):
        return reverse('products_by_category',args=[self.slug])



    def __str__(self):
        return self.name
    

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    name = models.CharField(max_length=100, unique=True, blank=False, null=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    
    image = models.ImageField(upload_to='product_images/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_available = models.BooleanField(default=True)


    @property
    def price_drop (self):
        if self.old_price and self.old_price > self.price:
            amount = self.old_price - self.price
            percentage = round((amount / self.old_price) * 100)

            return{'amount': amount, 'percentage': percentage}
        else:
            return None

        

    class Meta:
        verbose_name_plural = 'Products'

    def save(self,*args,**kwarges):
        if not self.slug:
            self.slug=slugify(self.name)
        super(Product,self).save(*args,**kwarges)

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="{}" width="50" height="50" />'.format(self.image.url))
        return ''

    

    def __str__(self):
        return self.name
    



class Banner(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='banner_images/', blank=True, null=True)
    show=models.BooleanField(default=True)
    created_date=models.DateTimeField(auto_now_add=True)

    def image_tag(self):
        if self.image:
            return mark_safe('<img src="{}" width="50" height="50" />'.format(self.image.url))
        return ''

    def __str__(self):
        return self.name