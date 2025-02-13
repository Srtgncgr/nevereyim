from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Address

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_verified', 'phone')
    list_filter = ('is_verified', 'is_staff', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Özel Alanlar', {'fields': ('phone', 'is_verified')}),
    )

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'full_name', 'is_default', 'created_at')
    list_filter = ('is_default', 'created_at')
    search_fields = ('user__username', 'full_name', 'full_address')
    raw_id_fields = ('user',)
