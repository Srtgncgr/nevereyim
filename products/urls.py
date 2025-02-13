from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('category/<slug:category_slug>/', views.category_products, name='category_products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('favorite/<int:product_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('is-favorite/<int:product_id>/', views.is_favorite, name='is_favorite'),
    path('favorites/', views.favorite_products, name='favorites'),
    path('all-products/', views.all_products, name='all_products'),
    path('search/', views.search_results, name='search_results'),
] 