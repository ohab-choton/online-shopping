from django.urls import path
from  . import views

urlpatterns = [
    path('place-order/', views.place_order , name='place-order'),
    path('proceed-payment/', views.proceed_to_payment, name='payment'),
    path('order_complete/', views.order_complete, name='order-complete'),
   
]

