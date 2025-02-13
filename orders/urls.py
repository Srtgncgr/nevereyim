from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.cart_detail, name='cart_detail'),
    path('add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('remove/<int:product_id>/', views.cart_remove, name='cart_remove'),
    path('create/', views.order_create, name='order_create'),
    path('history/', views.order_history, name='order_history'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
] 