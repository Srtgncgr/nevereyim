from django.http import JsonResponse
from .models import Product

class StockControlMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and 'cart/add_item' in request.path:
            try:
                product_id = request.POST.get('product_id')
                quantity = int(request.POST.get('quantity', 1))
                
                product = Product.objects.select_for_update().get(id=product_id)
                
                if product.stock < quantity:
                    return JsonResponse({
                        'error': f'Üzgünüz, {product.name} için yeterli stok bulunmuyor. Mevcut stok: {product.stock}'
                    }, status=400)
                    
            except Product.DoesNotExist:
                return JsonResponse({
                    'error': 'Ürün bulunamadı'
                }, status=404)
                
            except ValueError:
                return JsonResponse({
                    'error': 'Geçersiz miktar'
                }, status=400)
                
        return self.get_response(request) 