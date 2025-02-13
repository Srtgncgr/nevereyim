from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from .models import Category, Product, Favorite
from django.http import JsonResponse, Http404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_exempt
from django.db.models import Prefetch, Q
from django.template.loader import render_to_string
import logging
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError

# Create a logger
logger = logging.getLogger(__name__)

@ensure_csrf_cookie
def product_list(request):
    # Kategoriler ve temel ürün sorgusu
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)
    
    # Kategori bazlı filtreleme
    category_filter = request.GET.get('category')
    if category_filter and category_filter != 'all':
        products = products.filter(category__slug=category_filter)
    
    # Fiyat ve tarih bazlı sıralama
    sort_options = {
        'newest': '-created_at',
        'price_asc': 'price',
        'price_desc': '-price'
    }
    sort_param = request.GET.get('sort', 'newest')
    products = products.order_by(sort_options.get(sort_param, '-created_at'))
    
    # Sayfalama
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    products_page = paginator.get_page(page_number)
    
    context = {
        'categories': categories,
        'products': products_page,
        'current_category': category_filter,
        'current_sort': sort_param
    }
    
    return render(request, 'products/product_list.html', context)

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id)[:4]
    
    context = {
        'product': product,
        'related_products': related_products
    }
    return render(request, 'products/product_detail.html', context)

def category_products(request, category_slug):
    try:
        category = Category.objects.get(slug=category_slug)
        products = Product.objects.filter(category=category, is_active=True)
        
        # Kategoride ürün yoksa veya kategori bulunamazsa özel şablon
        if not products.exists():
            return render(request, 'products/category_empty.html', {
                'category': category,
                'categories': Category.objects.all(),
                'no_products': True
            })
        
        # Sayfalama
        paginator = Paginator(products, 12)  # Her sayfada 12 ürün
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'category': category,
            'products': page_obj,
            'categories': Category.objects.all(),
            'current_category': category_slug,
            'is_paginated': page_obj.has_other_pages()
        }
        
        return render(request, 'products/product_list.html', context)
    
    except Category.DoesNotExist:
        # Kategori bulunamazsa, tüm kategorileri göster
        return render(request, 'products/category_empty.html', {
            'category': None,
            'categories': Category.objects.all(),
            'category_not_found': True
        })

@login_required
@require_http_methods(["POST"])
def toggle_favorite(request, product_id):
    try:
        # Ürünün var olup olmadığını kontrol et
        product = get_object_or_404(Product, id=product_id)
        
        # Favoride zaten varsa kaldır, yoksa ekle
        try:
            favorite = Favorite.objects.get(user=request.user, product=product)
            # Zaten favoride ise sil
            favorite.delete()
            return JsonResponse({
                'status': 'removed', 
                'message': 'Üründen favoriler çıkarıldı'
            })
        except Favorite.DoesNotExist:
            # Favoride yoksa ekle
            Favorite.objects.create(user=request.user, product=product)
            return JsonResponse({
                'status': 'added', 
                'message': 'Ürün favorilere eklendi'
            })
    
    except Product.DoesNotExist:
        return JsonResponse({
            'status': 'error', 
            'message': 'Ürün bulunamadı'
        }, status=404)
    except ValidationError as e:
        return JsonResponse({
            'status': 'error', 
            'message': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error', 
            'message': 'Beklenmeyen bir hata oluştu'
        }, status=500)

@login_required
def favorite_products(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('product')
    
    context = {
        'favorites': favorites
    }
    return render(request, 'products/favorites.html', context)

@login_required
def is_favorite(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
        is_favorite = Favorite.objects.filter(
            user=request.user, 
            product=product
        ).exists()
        
        return JsonResponse({
            'is_favorite': is_favorite
        })
    except Product.DoesNotExist:
        return JsonResponse({
            'is_favorite': False
        }, status=404)

def all_products(request):
    categories = Category.objects.all()
    
    # Temel sorgu
    products = Product.objects.filter(is_active=True).select_related('category')
    
    # Resimleri ve favorileri önceden yükle
    products = products.prefetch_related(
        'images',
        'favorited_by'
    )
    
    # Kategoriye göre filtreleme
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    
    # Sıralama
    sort = request.GET.get('sort', '-created_at')
    if sort == 'price':
        products = products.order_by('price')
    elif sort == '-price':
        products = products.order_by('-price')
    else:
        products = products.order_by('-created_at')
    
    # Sayfalama
    paginator = Paginator(products, 12)  # Tüm ürünler sayfasında 12 ürün göster
    page = request.GET.get('page')
    products = paginator.get_page(page)
    
    context = {
        'categories': categories,
        'products': products,
        'current_category': category_slug,
        'current_sort': sort,
        'all_products_view': True  # Tüm ürünler sayfası olduğunu belirtmek için
    }
    return render(request, 'products/all_products.html', context)

def search_results(request):
    search_query = request.GET.get('search', '')
    
    logger.info(f"Search Query: {search_query}")  # Log the search query
    print(f"DEBUG: Search Query - {search_query}")  # Console log for immediate feedback
    
    # Kategorileri al
    categories = Category.objects.all()
    
    if not search_query:
        logger.warning("Empty search query")
        print("DEBUG: Empty search query")
        return render(request, 'products/search_results.html', {
            'products': [],
            'search_query': search_query,
            'categories': categories,
            'no_results': True
        })
    
    # Ürünlerde arama
    products = Product.objects.filter(
        Q(name__icontains=search_query) | 
        Q(category__name__icontains=search_query),
        is_active=True
    ).select_related('category').prefetch_related('images')
    
    logger.info(f"Total Products Found: {products.count()}")  # Log the total products found
    print(f"DEBUG: Total Products Found - {products.count()}")  # Console log
    
    # Sayfalama
    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products_page = paginator.get_page(page)
    
    context = {
        'products': products_page,
        'search_query': search_query,
        'total_results': products.count(),
        'categories': categories,
        'no_results': products.count() == 0
    }
    
    return render(request, 'products/search_results.html', context)
