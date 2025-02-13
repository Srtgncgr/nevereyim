from django.contrib import admin
from .models import Order, OrderItem, Cart, CartItem, Payment

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')

class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_price', 'status', 'phone', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__username', 'user__email', 'shipping_address', 'phone')
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    inlines = [OrderItemInline]
    fieldsets = (
        ('Müşteri Bilgileri', {
            'fields': ('user', 'phone')
        }),
        ('Sipariş Detayları', {
            'fields': ('total_price', 'status')
        }),
        ('Teslimat Bilgileri', {
            'fields': ('shipping_address', 'note')
        }),
        ('Tarih Bilgileri', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def has_add_permission(self, request):
        return False

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at', 'updated_at')
    search_fields = ('user__username', 'user__email')
    inlines = [CartItemInline]

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'amount', 'payment_method', 'status', 'created_at')
    list_filter = ('payment_method', 'status', 'created_at')
    search_fields = ('order__id', 'transaction_id', 'provider_ref')
    readonly_fields = ('created_at', 'updated_at')
