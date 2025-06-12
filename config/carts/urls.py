from django.urls import path
from  . import views

urlpatterns = [
    path('', views.cart_view, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),   
    path('update/<int:item_id>/', views.update_cart, name='update_cart'),
    path('remove/<int:item_id>/', views.remove_cart_item, name='remove_cart_item'),
    path('checkout/',views.get_checkout, name='checkout'),
]
