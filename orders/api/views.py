from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from ..models import Order, OrderItem, Cart as CartModel, CartItem, Product
from .serializers import OrderSerializer, CartSerializer, CartItemSerializer
from ..cart import Cart
from django.db.models import Prefetch
import logging
from rest_framework.exceptions import ValidationError

logger = logging.getLogger(__name__)

class OrderViewSet(viewsets.ModelViewSet):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.select_related('user').prefetch_related(
            Prefetch(
                'items',
                queryset=OrderItem.objects.select_related('product')
            )
        ).filter(user=self.request.user)

    def perform_create(self, serializer):
        try:
            cart = Cart(self.request)
            if not cart:
                raise ValidationError("Sepet boş")

            # Stok kontrolü
            for item in cart:
                if item['quantity'] > item['product'].stock:
                    raise ValidationError(
                        f"{item['product'].name} için yeterli stok yok"
                    )

            order = serializer.save(
                user=self.request.user,
                total_price=cart.get_total_price()
            )

            # İşlem loglaması
            logger.info(
                f"Order created: {order.id} by user {self.request.user.username}"
            )

            # Sepetteki ürünleri siparişe ekle
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                # Stok güncelleme
                product = item['product']
                product.stock -= item['quantity']
                product.save()

            # Sepeti temizle
            cart.clear()
            return order

        except Exception as e:
            logger.error(f"Error creating order: {e}")
            raise

    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        order = self.get_object()
        if order.status == 'pending':
            order.status = 'cancelled'
            order.save()
            return Response({'status': 'Order cancelled'})
        return Response(
            {'error': 'Order cannot be cancelled'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

class CartViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_cart(self, request):
        cart, created = CartModel.objects.get_or_create(user=request.user)
        return cart

    @action(detail=False, methods=['get'])
    def view_cart(self, request):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def add_item(self, request):
        cart = self.get_cart(request)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if quantity > product.stock:
            return Response(
                {'error': 'Not enough stock'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def update_quantity(self, request):
        cart = self.get_cart(request)
        product_id = request.data.get('product_id')
        quantity = int(request.data.get('quantity', 1))

        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product_id=product_id
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in cart'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        if quantity > cart_item.product.stock:
            return Response(
                {'error': 'Not enough stock'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if quantity <= 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def remove_item(self, request):
        cart = self.get_cart(request)
        product_id = request.data.get('product_id')

        try:
            cart_item = CartItem.objects.get(
                cart=cart,
                product_id=product_id
            )
        except CartItem.DoesNotExist:
            return Response(
                {'error': 'Item not found in cart'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        cart_item.delete()
        serializer = CartSerializer(cart)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def clear_cart(self, request):
        cart = self.get_cart(request)
        cart.items.all().delete()
        return Response({'message': 'Cart cleared'}) 