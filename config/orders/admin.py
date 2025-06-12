from django.contrib import admin
from .models import Order, Payment,OrderProduct
# Register your models here.

class OrderProductInLine(admin.TabularInline):
    model = OrderProduct
    readonly_fields = ['product', 'quantity', 'product_price', 'ordered','payment']
    fields = ['variation', 'product', 'quantity', 'product_price', 'ordered','payment']
    extra = 0

class OrderAdmin(admin.ModelAdmin):
    list_display = ['order_number', 'first_name', 'phone', 'email', 'city', 'order_total', 'is_ordered', 'shipping_cost', 'status', 'created_at']
    list_filter = ['status', 'is_ordered']
    search_fields = ['order_number', 'email']
    list_per_page = 20
    inlines = [OrderProductInLine]





admin.site.register(Order, OrderAdmin)

admin.site.register(Payment)
admin.site.register(OrderProduct)
