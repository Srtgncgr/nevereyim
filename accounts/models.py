from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True, verbose_name='Telefon')
    is_verified = models.BooleanField(default=False, verbose_name='Doğrulanmış Kullanıcı')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')

    # related_name'leri ekleyin
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',
        related_query_name='custom_user'
    )

    class Meta:
        verbose_name = 'Kullanıcı'
        verbose_name_plural = 'Kullanıcılar'
        
    def __str__(self):
        return self.email or self.username

# Diğer kodlar aynı kalacak

class Address(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='addresses')
    title = models.CharField('Adres Başlığı', max_length=100, help_text='Ev, İş vb.')
    full_name = models.CharField('Ad Soyad', max_length=150)
    phone = models.CharField('Telefon Numarası', max_length=20)
    city = models.CharField('Şehir', max_length=100, null=True, blank=True)
    district = models.CharField('İlçe', max_length=100, null=True, blank=True)
    full_address = models.TextField('Tam Adres')
    is_default = models.BooleanField('Varsayılan Adres', default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Adres'
        verbose_name_plural = 'Adresler'
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.full_name}"

    def save(self, *args, **kwargs):
        # Eğer bu adres varsayılan olarak işaretlendiyse, 
        # diğer adreslerin varsayılan durumunu kaldır
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)