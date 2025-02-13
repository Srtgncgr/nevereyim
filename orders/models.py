from django.db import models
from django.conf import settings
from products.models import Product

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Beklemede'),
        ('processing', 'İşleniyor'),
        ('shipped', 'Kargoya Verildi'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'İptal Edildi'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Kullanıcı')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Toplam Fiyat')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Durum')
    shipping_address = models.TextField(verbose_name='Teslimat Adresi')
    phone = models.CharField(max_length=20, verbose_name='Telefon')
    note = models.TextField(blank=True, null=True, verbose_name='Sipariş Notu')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sipariş'
        verbose_name_plural = 'Siparişler'
        ordering = ['-created_at']

    def __str__(self):
        return f"Sipariş #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Sipariş')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Ürün')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Adet')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Fiyat')

    class Meta:
        verbose_name = 'Sipariş Ürünü'
        verbose_name_plural = 'Sipariş Ürünleri'

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Kullanıcı')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Sepet'
        verbose_name_plural = 'Sepetler'

    def __str__(self):
        return f"{self.user.username}'in Sepeti"
    
    @property
    def total(self):
        return sum(item.product.price * item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name='Sepet')
    product = models.ForeignKey('products.Product', on_delete=models.CASCADE, verbose_name='Ürün')
    quantity = models.PositiveIntegerField(default=1, verbose_name='Adet')

    class Meta:
        verbose_name = 'Sepet Ürünü'
        verbose_name_plural = 'Sepet Ürünleri'

    def __str__(self):
        return f"{self.quantity}x {self.product.name}"

class Payment(models.Model):
    PAYMENT_STATUS = (
        ('pending', 'Beklemede'),
        ('processing', 'İşleniyor'),
        ('completed', 'Tamamlandı'),
        ('failed', 'Başarısız'),
        ('refunded', 'İade Edildi'),
    )
    
    PAYMENT_METHOD = (
        ('credit_card', 'Kredi Kartı'),
        ('bank_transfer', 'Havale/EFT'),
        ('pay_at_door', 'Kapıda Ödeme'),
    )

    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Tutar')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD, verbose_name='Ödeme Yöntemi')
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', verbose_name='Durum')
    transaction_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='İşlem No')
    provider_ref = models.CharField(max_length=100, blank=True, null=True, verbose_name='Ödeme Sağlayıcı Referansı')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Ödeme'
        verbose_name_plural = 'Ödemeler'

    def __str__(self):
        return f"Ödeme #{self.id} - {self.order.id}"
