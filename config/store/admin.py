from django.contrib import admin
from .models import Category,Product,Banner

# Register your models here.
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',  'image_tag')
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'category', 'price', 'stock', 'is_available', 'image_tag')
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ('category', 'is_available')
    search_fields = ('name', 'description')
    list_editable = ('price', 'stock', 'is_available')

admin.site.register(Product, ProductAdmin)
admin.site.register(Banner)

