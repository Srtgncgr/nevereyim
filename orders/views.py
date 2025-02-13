from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from products.models import Product
from .models import Cart, CartItem, Order, OrderItem
from .cart import Cart
from django.db import transaction
from django.core.exceptions import ValidationError

@login_required
def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        print(f"Ürün: {item.get('product', None)}, Miktar: {item.get('quantity', 0)}")  # Debug için
    return render(request, 'orders/cart_detail.html', {
        'cart_items': cart,
        'cart_total': cart.get_total_price()
    })

@login_required
def cart_add(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart.add(product=product, quantity=quantity)
        messages.success(request, 'Ürün sepete eklendi.')
    
    return redirect('products:product_detail', slug=product.slug)

@login_required
def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    cart.remove(product)
    request.session.modified = True  # Session'ı güncelle
    messages.success(request, 'Ürün sepetten kaldırıldı.')
    return redirect('orders:cart_detail')

@login_required
def cart_update(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart.add(product=product, quantity=quantity, override_quantity=True)
        messages.success(request, 'Sepet güncellendi.')
    
    return redirect('orders:cart_detail')

@login_required
def order_create(request):
    cart = Cart(request)
    cart_items = list(cart)  # Sepet öğelerini liste olarak al

    if not cart_items:
        messages.error(request, 'Sepetiniz boş!')
        return redirect('orders:cart_detail')

    context = {
        'cart_items': cart_items,
        'cart_total': cart.get_total_price()
    }

    if request.method == 'POST':
        # Tüm ürünler için stok kontrolü
        for item in cart_items:
            product = item['product']
            quantity = item['quantity']
            try:
                product.check_stock(quantity)
            except ValidationError as e:
                messages.error(request, str(e))
                return redirect('orders:cart_detail')

        # Sipariş oluştur
        total_price = cart.get_total_price()
        order = Order.objects.create(
            user=request.user,
            total_price=total_price,
            shipping_address=request.POST.get('shipping_address'),
            phone=request.POST.get('phone'),
            note=request.POST.get('note')
        )

        # Sipariş detaylarını oluştur ve stokları güncelle
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price']
            )
            # Stok güncelle
            item['product'].decrease_stock(item['quantity'])

        # Sepeti temizle
        cart.clear()

        messages.success(request, 'Siparişiniz başarıyla oluşturuldu.')
        return redirect('orders:order_history')

    return render(request, 'orders/order_create.html', context)

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_history.html', {'orders': orders})
