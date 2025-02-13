"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter  # rest_framework.routers altı sarı çizgili çünkü settings.py'da rest_framework uygulaması INSTALLED_APPS listesine eklenmiş ama henüz pip ile rest_framework paketi yüklenmemiş olabilir. Bu sorunu çözmek için terminal'de "pip install djangorestframework" komutunu çalıştırmanız gerekiyor.
from products.api.views import ProductViewSet, CategoryViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from orders.api.views import OrderViewSet, CartViewSet
from accounts.api.views import UserProfileViewSet

# API Router
router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='api_product')
router.register(r'categories', CategoryViewSet, basename='api_category')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'profile', UserProfileViewSet, basename='profile')
router.register(r'cart', CartViewSet, basename='cart')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('products.urls', namespace='products')),  # namespace ekledik
    path('accounts/', include('accounts.urls')),
    path('orders/', include('orders.urls')),
    
    # API URLs - farklı bir namespace ile
    path('api/', include((router.urls, 'api'), namespace='api')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api-auth/', include('rest_framework.urls')),
]

# Media dosyaları için URL yapılandırması
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
