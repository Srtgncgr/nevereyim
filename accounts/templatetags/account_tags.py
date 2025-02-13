from django import template

register = template.Library()

@register.filter
def status_color(status):
    """Sipariş durumuna göre renk döndürür"""
    colors = {
        'pending': 'warning',      # Beklemede
        'processing': 'info',      # İşleniyor
        'shipped': 'primary',      # Kargoya Verildi
        'delivered': 'success',    # Teslim Edildi
        'cancelled': 'danger',     # İptal Edildi
    }
    return colors.get(status, 'secondary')

@register.filter
def multiply(value, arg):
    """İki sayıyı çarpar"""
    return float(value) * float(arg) 