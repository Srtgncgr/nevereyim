from django.db import models, transaction
from django.utils.text import slugify
from django.conf import settings
from django.core.exceptions import ValidationError

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name='Kategori Adı')
    slug = models.SlugField(unique=True, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, 
                             related_name='children', verbose_name='Üst Kategori')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    image = models.ImageField(upload_to='categories/', blank=True, null=True, verbose_name='Görsel')
    image_url = models.URLField(max_length=1000, blank=True, null=True, verbose_name='Görsel URL')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Kategori'
        verbose_name_plural = 'Kategoriler'
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name
    
    def get_image(self):
        return self.image_url if self.image_url else self.image.url if self.image else None

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name='Kategori')
    name = models.CharField(max_length=200, verbose_name='Ürün Adı')
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(verbose_name='Açıklama')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Fiyat')
    stock = models.PositiveIntegerField(default=0, verbose_name='Stok')
    is_active = models.BooleanField(default=True, verbose_name='Aktif mi?')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Ürün'
        verbose_name_plural = 'Ürünler'
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

    def check_stock(self, quantity):
        """Stok kontrolü yapar"""
        if self.stock < quantity:
            raise ValidationError(
                f'Üzgünüz, {self.name} için yeterli stok bulunmuyor. '
                f'Mevcut stok: {self.stock}'
            )
        return True

    @transaction.atomic
    def decrease_stock(self, quantity):
        """Stok miktarını güvenli bir şekilde azaltır"""
        if self.check_stock(quantity):
            self.stock -= quantity
            self.save()
            
            # Eğer stok kritik seviyenin altına düştüyse bildirim gönder
            if self.stock <= 5:
                self.send_low_stock_notification()
                
    def send_low_stock_notification(self):
        """Düşük stok bildirimi gönderir"""
        # Burada email veya başka bir bildirim sistemi kullanılabilir
        print(f'Düşük stok uyarısı: {self.name} - Kalan stok: {self.stock}')

    def is_favorite_of(self, user):
        """Ürünün kullanıcının favorilerinde olup olmadığını kontrol eder"""
        if user.is_authenticated:
            return self.favorited_by.filter(user=user).exists()
        return False

    @property
    def favorited_users(self):
        """Bu ürünü favorileyen kullanıcıları döndürür"""
        return [favorite.user for favorite in self.favorited_by.all()]

class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image_url = models.URLField(verbose_name='Görsel URL', default='http://example.com/default.jpg')
    is_main = models.BooleanField(default=False, verbose_name='Ana Görsel')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_image(self):
        return self.image_url

    class Meta:
        verbose_name = 'Ürün Görseli'
        verbose_name_plural = 'Ürün Görselleri'
        ordering = ['-is_main', '-created_at']

    def __str__(self):
        return f"{self.product.name} - Görsel {self.id}"

class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Favori'
        verbose_name_plural = 'Favoriler'
        unique_together = ['user', 'product']  # Bir ürün sadece bir kez favorilere eklenebilir

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class Review(models.Model):
    RATING_CHOICES = (
        (1, '1 Yıldız'),
        (2, '2 Yıldız'),
        (3, '3 Yıldız'),
        (4, '4 Yıldız'),
        (5, '5 Yıldız'),
    )

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Puan')
    comment = models.TextField(verbose_name='Yorum')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_approved = models.BooleanField(default=False, verbose_name='Onaylı')

    class Meta:
        verbose_name = 'Değerlendirme'
        verbose_name_plural = 'Değerlendirmeler'
        ordering = ['-created_at']
        unique_together = ['user', 'product']  # Bir kullanıcı bir ürüne sadece bir değerlendirme yapabilir

    def __str__(self):
        return f"{self.user.username} - {self.product.name} - {self.rating}★"
