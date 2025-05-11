from django.urls import path
from . import views



urlpatterns = [
    path('', views.index, name='index'),
    path('product_details/<slug:slug>/', views.product_details, name='product_details'),
    path('store/', views.store, name='store'),
    path('catagory/<slug:category_slug>/', views.products_by_category, name='products_by_category'),
   
 
]
