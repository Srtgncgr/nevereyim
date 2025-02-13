from django import template
from products.models import Favorite

register = template.Library()

@register.filter
def is_favorite_of(product, user):
    if user.is_authenticated:
        return Favorite.objects.filter(user=user, product=product).exists()
    return False 