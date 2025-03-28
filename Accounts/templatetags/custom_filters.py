from django import template
from django.db.models import F, Sum, Q

register = template.Library()

@register.filter
def sum_total(products):
    """Calculate the sum of total field for all products"""
    if not products:
        return 0
    return sum(product.total for product in products if hasattr(product, 'total'))

@register.filter
def filter_low_stock(products):
    """Filter products with low stock"""
    if not products:
        return []
    return [p for p in products if p.current_stock <= p.threshold and p.current_stock > 0]