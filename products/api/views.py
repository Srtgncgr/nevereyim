from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from ..models import Product, Category, ProductImage
from .serializers import ProductSerializer, CategorySerializer
from django.db.models import Prefetch
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework.exceptions import ValidationError
from django.core.exceptions import ObjectDoesNotExist
import logging

logger = logging.getLogger(__name__)

class ProductViewSet(viewsets.ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug'
    
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'price', 'is_active']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['price', 'created_at', 'name']
    ordering = ['-created_at']  # varsayılan sıralama

    def get_queryset(self):
        queryset = Product.objects.select_related('category').prefetch_related(
            Prefetch('images', queryset=ProductImage.objects.filter(is_main=True)),
            'reviews'
        ).filter(is_active=True)
        
        category = self.request.query_params.get('category', None)
        if category:
            queryset = queryset.filter(category__slug=category)
        
        return queryset

    @method_decorator(cache_page(60 * 15))  # 15 dakika cache
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(60 * 60))  # 1 saat cache
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        featured_products = self.get_queryset().filter(is_featured=True)
        serializer = self.get_serializer(featured_products, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def by_price_range(self, request):
        min_price = request.query_params.get('min', None)
        max_price = request.query_params.get('max', None)
        
        queryset = self.get_queryset()
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except ValidationError as e:
            logger.error(f"Validation error while creating product: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while creating product: {e}")
            raise

    def update(self, request, *args, **kwargs):
        try:
            return super().update(request, *args, **kwargs)
        except ObjectDoesNotExist as e:
            logger.error(f"Product not found: {e}")
            raise NotFound("Ürün bulunamadı")
        except Exception as e:
            logger.error(f"Error updating product: {e}")
            raise

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field = 'slug' 